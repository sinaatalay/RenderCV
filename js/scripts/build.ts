// Build the npm package: RenderCV's wheel and its dependencies, the version,
// and the JavaScript.
//
// 1. Takes the version from `pyproject.toml`, so the npm package and the
//    Python package always have the same version.
// 2. Builds RenderCV's wheel with uv.
// 3. Resolves RenderCV's dependencies for Pyodide with micropip, once, here,
//    and puts every wheel in `wheels/`, listed in `wheels/manifest.json`:
//    those from PyPI and those Pyodide distributes. So the package loads
//    exactly the versions it was tested with and downloads no Python
//    packages. Only RenderCV's fonts, which are optional, are downloaded
//    when used.
// 4. Compiles `src/` to `dist/` with TypeScript.

import { createHash } from "node:crypto";
import { access, mkdtemp, readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { $ } from "bun";
import { loadPyodide, version as pyodideVersion } from "pyodide";

import type { Manifest } from "../src/index.ts";

const packageFolder = join(import.meta.dir, "..");
const repositoryRoot = join(packageFolder, "..");
const wheelsFolder = join(packageFolder, "wheels");

const pyproject = await Bun.file(join(repositoryRoot, "pyproject.toml")).text();
const version = pyproject.match(/^version = "(.+)"$/m)?.[1];
if (version === undefined) {
  throw new Error("Couldn't find the version in pyproject.toml.");
}

await Bun.write(
  join(packageFolder, "src", "version.ts"),
  "// The version of RenderCV this package runs. `bun run build` sets it from\n" +
    "// pyproject.toml; a test checks that it's up to date.\n" +
    `export const version = "${version}";\n`,
);
const packageJsonFile = Bun.file(join(packageFolder, "package.json"));
const packageJson = await packageJsonFile.json();
if (packageJson.version !== version) {
  packageJson.version = version;
  await Bun.write(packageJsonFile, `${JSON.stringify(packageJson, null, 2)}\n`);
}

await rm(wheelsFolder, { recursive: true, force: true });
const buildFolder = await mkdtemp(join(tmpdir(), "rendercv-wheel-"));
let rendercvWheel: string;
try {
  await $`uv build --wheel --out-dir ${buildFolder}`.cwd(repositoryRoot).quiet();
  const wheelName = (await readdir(buildFolder)).find((name) => name.endsWith(".whl"));
  if (wheelName === undefined) {
    throw new Error("uv didn't build a wheel.");
  }
  rendercvWheel = wheelName;
  await Bun.write(join(wheelsFolder, wheelName), Bun.file(join(buildFolder, wheelName)));
} finally {
  await rm(buildFolder, { recursive: true, force: true });
}

// Resolve the dependencies the way the package would at runtime:
type LockedPackage = { name: string; version: string; file_name: string; sha256: string; depends: string[] };
const pyodide = await loadPyodide();
pyodide.FS.mkdirTree("/tmp/wheels");
pyodide.FS.writeFile(`/tmp/wheels/${rendercvWheel}`, await Bun.file(join(wheelsFolder, rendercvWheel)).bytes());
await pyodide.loadPackage("micropip", { messageCallback: () => {} });
const lockJson: string = await pyodide.runPythonAsync(`
import micropip

# micropip doesn't install the email extra of pydantic[email]; rendercv-fonts
# is RenderCV's "full" extra:
await micropip.install(["emfs:/tmp/wheels/${rendercvWheel}", "email-validator", "rendercv-fonts"])
micropip.freeze()
`);
const normalize = (name: string) => name.toLowerCase().replace(/[-_.]+/g, "-");
const locked = new Map<string, LockedPackage>(
  Object.values(JSON.parse(lockJson).packages as Record<string, LockedPackage>).map((entry) => [
    normalize(entry.name),
    entry,
  ]),
);
const closure = (roots: string[]) => {
  const names = new Set<string>();
  const visit = (name: string) => {
    const normalized = normalize(name);
    if (names.has(normalized)) return;
    const entry = locked.get(normalized);
    if (entry === undefined) throw new Error(`micropip didn't resolve ${name}.`);
    names.add(normalized);
    entry.depends.forEach(visit);
  };
  roots.forEach(visit);
  return [...names].map((name) => locked.get(name)!);
};
const isFromPyPI = (entry: LockedPackage) => entry.file_name.startsWith("https://");

/**
 * A wheel's bytes. Wheels from PyPI are downloaded; wheels Pyodide
 * distributes are where Pyodide cached them in Node.js, or on its CDN.
 */
async function wheelBytes(entry: LockedPackage, fileName: string): Promise<Uint8Array> {
  if (!isFromPyPI(entry)) {
    try {
      await access(entry.file_name);
      return await Bun.file(entry.file_name).bytes();
    } catch {
      // Not cached; download it below.
    }
  }
  const url = isFromPyPI(entry) ? entry.file_name : `https://cdn.jsdelivr.net/pyodide/v${pyodideVersion}/full/${fileName}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Couldn't download ${url}: ${response.status}.`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

const manifest: Manifest = { rendercv: version, pyodide: pyodideVersion, wheels: [rendercvWheel] };
for (const entry of closure(["rendercv", "email-validator"])) {
  if (normalize(entry.name) === "rendercv") continue;
  const fileName = decodeURIComponent(entry.file_name.split("/").pop()!);
  const bytes = await wheelBytes(entry, fileName);
  if (createHash("sha256").update(bytes).digest("hex") !== entry.sha256) {
    throw new Error(`${fileName} doesn't have the SHA-256 it's locked with.`);
  }
  await Bun.write(join(wheelsFolder, fileName), bytes);
  manifest.wheels.push(fileName);
}
const [fonts, ...fontDependencies] = closure(["rendercv-fonts"]);
if (fonts === undefined || fontDependencies.length > 0 || !isFromPyPI(fonts)) {
  throw new Error("rendercv-fonts should be one wheel from PyPI, without dependencies.");
}
manifest.fonts = {
  url: fonts.file_name,
  fileName: decodeURIComponent(fonts.file_name.split("/").pop()!),
  sha256: fonts.sha256,
};
await Bun.write(join(wheelsFolder, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);

await rm(join(packageFolder, "dist"), { recursive: true, force: true });
await $`tsc -p tsconfig.build.json`.cwd(packageFolder);

console.log(`Built rendercv ${version} with ${manifest.wheels.length} wheels for Pyodide ${pyodideVersion}.`);
