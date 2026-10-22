// RenderCV for JavaScript: the same RenderCV as the command line, running in
// Pyodide (Python compiled to WebAssembly), in Node.js, Bun, and browsers.
//
// ```js
// import { loadRenderCV } from "rendercv";
//
// const rendercv = await loadRenderCV();
// const cv = await rendercv.render({ yaml: "cv:\n  name: Jane Doe\n" });
// // cv.pdf is a Uint8Array
// ```

import { loadPyodide, version as pyodideVersion, type PyodideAPI } from "pyodide";

import { glue } from "./python.js";
import { version } from "./version.js";

export { version };

/** A format RenderCV renders a CV to. */
export type OutputFormat = "pdf" | "png" | "svg" | "html" | "markdown" | "typst";

/** The formats RenderCV renders to. */
export const outputFormats: readonly OutputFormat[] = [
  "pdf",
  "png",
  "svg",
  "html",
  "markdown",
  "typst",
];

/** Options for loading RenderCV. */
export interface LoadOptions {
  /**
   * A Pyodide to install RenderCV into, for example one your app already
   * uses. By default, a new one is loaded.
   */
  pyodide?: PyodideAPI;
  /**
   * Where Pyodide's files are, if a new Pyodide is loaded. In Node.js and Bun,
   * they come from the `pyodide` package; in browsers, from the jsDelivr CDN
   * by default.
   */
  indexURL?: string;
  /**
   * The folder with the wheels of RenderCV and its dependencies, and their
   * `manifest.json`. By default, the `wheels` folder of this package.
   */
  wheelsURL?: string | URL;
  /**
   * Whether to install RenderCV's fonts (the `rendercv-fonts` Python package,
   * a 33 MB download), so CVs look exactly as they do with the command line.
   * Without them, Typst's built-in fonts are used, and the icons of the
   * designs are missing. Fonts can also be given with a project's `files`.
   * In Node.js and Bun, the download is kept in this package's `.cache`
   * folder, so it happens once. Default: `true`.
   */
  fonts?: boolean;
}

/** A CV: the files RenderCV reads, as their contents. */
export interface Project {
  /** The YAML input file. */
  yaml: string;
  /** `design.typ`. By default, the classic design. */
  design?: string;
  /** `entries.typ`. By default, the standard entry types. */
  entries?: string;
  /**
   * Other files the CV uses, by their paths relative to the YAML file: a
   * photo (`"photo.jpg"`), fonts (`"fonts/Inter-Regular.ttf"`), or Typst files
   * that `design.typ` or `entries.typ` import.
   */
  files?: Record<string, string | Uint8Array>;
  /**
   * Values that replace the YAML's, by their places in it, like
   * `{ "cv.name": "Jane Doe" }`. Same as `rendercv render --cv.name "Jane Doe"`.
   */
  overrides?: Record<string, string>;
}

/** The outputs of a render. Formats that weren't asked for are missing. */
export interface RenderedCV {
  pdf?: Uint8Array;
  /** One image per page. */
  png?: Uint8Array[];
  /** One image per page. */
  svg?: string[];
  html?: string;
  markdown?: string;
  /** The Typst source, which compiles on its own with Typst. */
  typst?: string;
}

/** Something wrong with a CV, and where it is. */
export interface Problem {
  message: string;
  /**
   * The YAML file the problem is in: `"input"`, or a locale or settings
   * overlay. Missing for problems outside the YAML, like errors in
   * `design.typ`, whose messages say where they are.
   */
  source?: "input" | "locale" | "settings";
  /** The keys leading to the problem, like `["cv", "sections", "education", "0"]`. */
  path: string[];
  /** Where the problem is in the YAML, counting from 1. */
  line?: number;
  column?: number;
  endLine?: number;
  endColumn?: number;
}

/** Thrown by `render` when a CV has problems. */
export class RenderCVError extends Error {
  readonly problems: Problem[];

  constructor(problems: Problem[]) {
    super(problems.map((problem) => problem.message).join("\n"));
    this.name = "RenderCVError";
    this.problems = problems;
  }
}

/**
 * What `wheels/manifest.json` lists: the wheels to load, which `bun run build`
 * resolved for this Pyodide version.
 */
export interface Manifest {
  /** The RenderCV version. */
  rendercv: string;
  /** The Pyodide version the wheels were resolved for. */
  pyodide: string;
  /** Wheels in the `wheels` folder: RenderCV's and all its dependencies'. */
  wheels: string[];
  /** RenderCV's fonts on PyPI, loaded only if asked for. */
  fonts?: { url: string; fileName: string; sha256: string };
}

type PythonFunction = ((...args: unknown[]) => { toJs(options: object): unknown; destroy(): void }) & {
  destroy(): void;
};

interface PythonResult {
  outputs?: RenderedCV;
  problems?: RawProblem[];
}

type RawProblem = { [key in keyof Problem]?: Problem[key] | null };

const isServerRuntime =
  typeof process !== "undefined" && typeof process.versions?.node === "string";

/** Read a file from a URL: `file:` URLs from disk, others with `fetch`. */
async function readBytes(url: URL): Promise<Uint8Array<ArrayBuffer>> {
  if (url.protocol === "file:") {
    const fs: typeof import("node:fs/promises") = await importNodeModule("node:fs/promises");
    return new Uint8Array(await fs.readFile(url));
  }
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Couldn't download ${url}: ${response.status} ${response.statusText}`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

// Node.js modules, hidden from bundlers, which would try to bundle them:
const importNodeModule = (name: string): Promise<any> => import(/* @vite-ignore */ name);

/** Where `loadPackage` loads a file from: a path in Node.js, a URL elsewhere. */
async function packageLocation(url: URL): Promise<string> {
  if (url.protocol !== "file:") return url.href;
  // Pyodide reads `file:` URLs wrong on Windows, but plain paths right:
  const { fileURLToPath } = await importNodeModule("node:url");
  return fileURLToPath(url);
}

/**
 * Where to load RenderCV's fonts from. In Node.js and Bun, the wheel is
 * downloaded once and kept in this package's `.cache` folder; in browsers,
 * the browser's cache keeps it.
 */
async function fontsLocation(fonts: NonNullable<Manifest["fonts"]>): Promise<string> {
  const cacheURL = new URL("../.cache/", import.meta.url);
  if (cacheURL.protocol !== "file:") return fonts.url;
  const fs: typeof import("node:fs/promises") = await importNodeModule("node:fs/promises");
  const file = new URL(fonts.fileName, cacheURL);
  try {
    await fs.access(file);
    return packageLocation(file);
  } catch {
    // Not downloaded yet.
  }
  const bytes = await readBytes(new URL(fonts.url));
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  const sha256 = Array.from(digest, (byte) => byte.toString(16).padStart(2, "0")).join("");
  if (sha256 !== fonts.sha256) {
    throw new Error(`${fonts.fileName} doesn't have the SHA-256 it should have.`);
  }
  try {
    await fs.mkdir(cacheURL, { recursive: true });
    await fs.writeFile(file, bytes);
    return packageLocation(file);
  } catch {
    // The package folder is read-only; download it every time.
    return fonts.url;
  }
}

/** Turn a problem from Python into a `Problem`, leaving out `None`s. */
function toProblem(raw: RawProblem): Problem {
  const problem: Problem = { message: raw.message ?? "", path: raw.path ?? [] };
  if (raw.source != null) problem.source = raw.source;
  if (raw.line != null) problem.line = raw.line;
  if (raw.column != null) problem.column = raw.column;
  if (raw.endLine != null) problem.endLine = raw.endLine;
  if (raw.endColumn != null) problem.endColumn = raw.endColumn;
  return problem;
}

/** Check that a project file's path stays inside the project. */
function checkRelativePath(path: string): string[] {
  const parts = path.split(/[\\/]/).filter((part) => part !== "" && part !== ".");
  if (/^([a-zA-Z]:|[\\/])/.test(path) || parts.includes("..") || parts.length === 0) {
    throw new Error(`The file path "${path}" should be relative to the YAML file, without "..".`);
  }
  return parts;
}

/** RenderCV, loaded and ready to render. Create it with `loadRenderCV`. */
export class RenderCV {
  /** The version of RenderCV. */
  readonly version = version;
  /** The Pyodide RenderCV runs in. */
  readonly pyodide: PyodideAPI;

  #functions: Map<string, PythonFunction>;
  // Renders run one at a time, since they share Pyodide's file system:
  #queue: Promise<unknown> = Promise.resolve();

  /** @internal Use `loadRenderCV`. */
  constructor(pyodide: PyodideAPI, functions: Map<string, PythonFunction>) {
    this.pyodide = pyodide;
    this.#functions = functions;
  }

  /**
   * Render a CV.
   *
   * @param project The CV's files.
   * @param options.formats The formats to render to. Default: `["pdf"]`.
   * @throws {RenderCVError} If the CV has problems.
   */
  async render(project: Project, options: { formats?: OutputFormat[] } = {}): Promise<RenderedCV> {
    const formats = options.formats ?? ["pdf"];
    const unknown = formats.filter((format) => !outputFormats.includes(format));
    if (unknown.length > 0) {
      throw new Error(`Unknown output formats: ${unknown.join(", ")}. Available formats: ${outputFormats.join(", ")}.`);
    }
    const result = await this.#run(project, "render_project", formats) as PythonResult;
    if (result.problems !== undefined) {
      throw new RenderCVError(result.problems.map(toProblem));
    }
    return result.outputs ?? {};
  }

  /**
   * Check a CV without rendering it.
   *
   * @param project The CV's files.
   * @returns The problems; empty if the CV is valid.
   */
  async validate(project: Project): Promise<Problem[]> {
    const problems = await this.#run(project, "validate_project") as RawProblem[];
    return problems.map(toProblem);
  }

  #run(project: Project, functionName: string, ...args: unknown[]): Promise<unknown> {
    const run = async () => {
      this.#writeProject(project);
      const overrides = this.pyodide.toPy(project.overrides ?? {});
      const pythonArgs = args.map((arg) => this.pyodide.toPy(arg));
      try {
        const result = this.#functions.get(functionName)!(...pythonArgs, overrides);
        try {
          return result.toJs({ dict_converter: Object.fromEntries, create_pyproxies: false });
        } finally {
          result.destroy();
        }
      } finally {
        overrides.destroy();
        for (const arg of pythonArgs) arg.destroy();
      }
    };
    const job = this.#queue.then(run, run);
    this.#queue = job.catch(() => undefined);
    return job;
  }

  #writeProject(project: Project) {
    const folder = String(this.#functions.get("reset_project_folder")!());
    const files: [string, string | Uint8Array][] = [
      ...Object.entries(project.files ?? {}),
      ["cv.yaml", project.yaml],
    ];
    if (project.design !== undefined) files.push(["design.typ", project.design]);
    if (project.entries !== undefined) files.push(["entries.typ", project.entries]);
    for (const [path, content] of files) {
      const parts = checkRelativePath(path);
      if (parts.length > 1) {
        this.pyodide.FS.mkdirTree([folder, ...parts.slice(0, -1)].join("/"));
      }
      this.pyodide.FS.writeFile([folder, ...parts].join("/"), content);
    }
  }
}

/**
 * Load Pyodide, install RenderCV into it, and return it ready to render.
 *
 * Loading takes a few seconds (Pyodide, RenderCV, its dependencies, and fonts
 * are downloaded); rendering takes a fraction of a second. Load once and
 * render many times. Pyodide runs on the thread it's loaded in, so in browsers
 * load it in a Web Worker to keep pages responsive.
 */
export async function loadRenderCV(options: LoadOptions = {}): Promise<RenderCV> {
  const pyodide =
    options.pyodide ??
    (await loadPyodide({
      indexURL:
        options.indexURL ??
        (isServerRuntime ? undefined : `https://cdn.jsdelivr.net/pyodide/v${pyodideVersion}/full/`),
    }));

  const wheelsURL = new URL(options.wheelsURL ?? new URL("../wheels/", import.meta.url));
  if (!wheelsURL.pathname.endsWith("/")) wheelsURL.pathname += "/";
  const manifest: Manifest = JSON.parse(new TextDecoder().decode(await readBytes(new URL("manifest.json", wheelsURL))));
  if (manifest.pyodide.split(".")[0] !== pyodide.version.split(".")[0]) {
    throw new Error(
      `RenderCV's wheels are for Pyodide ${manifest.pyodide}, but Pyodide ${pyodide.version} is loaded.`,
    );
  }
  const wheels = await Promise.all(manifest.wheels.map((wheel) => packageLocation(new URL(wheel, wheelsURL))));
  const quiet = { messageCallback: () => {} };
  await pyodide.loadPackage(wheels, quiet);
  if ((options.fonts ?? true) && manifest.fonts !== undefined) {
    await pyodide.loadPackage(await fontsLocation(manifest.fonts), quiet);
  }

  const namespace = pyodide.toPy({});
  try {
    pyodide.runPython(glue, { globals: namespace });
    const functions = new Map<string, PythonFunction>();
    for (const name of ["reset_project_folder", "render_project", "validate_project"]) {
      functions.set(name, namespace.get(name));
    }
    return new RenderCV(pyodide, functions);
  } finally {
    namespace.destroy();
  }
}
