import { beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";

import { loadRenderCV, outputFormats, RenderCV, RenderCVError, version } from "../src/index.ts";

// Loading downloads Pyodide's packages and RenderCV's dependencies:
setDefaultTimeout(300_000);

const yaml = `cv:
  name: Jane Doe
  email: jane@example.com
  sections:
    Skills:
      - bullet: Typst **and** YAML
settings:
  current_date: 2024-06-15
`;

const designFor = (name: string) =>
  `#import "@preview/rendercv:${version}": designs\n#let design = designs.${name}()\n`;

const text = (bytes: Uint8Array) => new TextDecoder("latin1").decode(bytes);

let rendercv: RenderCV;

beforeAll(async () => {
  // Fonts are tested in fonts.test.ts; without them, loading is faster:
  rendercv = await loadRenderCV({ fonts: false });
});

describe("render", () => {
  test("renders a PDF by default", async () => {
    const cv = await rendercv.render({ yaml });

    expect(text(cv.pdf!.subarray(0, 5))).toBe("%PDF-");
    expect(Object.keys(cv)).toEqual(["pdf"]);
  });

  test("renders every format", async () => {
    const cv = await rendercv.render({ yaml }, { formats: [...outputFormats] });

    expect(cv.pdf).toBeInstanceOf(Uint8Array);
    expect(cv.png).toHaveLength(1);
    expect(text(cv.png![0]!.subarray(1, 4))).toBe("PNG");
    expect(cv.svg![0]).toStartWith("<svg");
    expect(cv.html).toContain("Jane Doe");
    expect(cv.markdown).toStartWith("# Jane Doe");
    expect(cv.markdown).toContain("Typst **and** YAML");
    expect(cv.typst).toContain(`#import "@preview/rendercv:${version}" as rendercv`);
  });

  test("uses the design", async () => {
    const cv = await rendercv.render({ yaml, design: designFor("moderncv") }, { formats: ["typst"] });

    expect(cv.typst).toContain('#import "/design.typ" as design-file');
  });

  test("uses the entry types", async () => {
    const entries = `#import "@preview/rendercv:${version}": *
#let talk = entry-type(
  fields: (title: field("markdown"), event: field("markdown")),
  look: (it, ctx) => as-entry("normal", name: [#it.title at #it.event]),
)
`;
    const talkYaml = `cv:
  name: Jane Doe
  sections:
    Talks:
      - title: Typst for CVs
        event: PyCon
`;

    const cv = await rendercv.render({ yaml: talkYaml, entries }, { formats: ["markdown"] });

    expect(cv.markdown).toContain("Typst for CVs at PyCon");
  });

  test("forgets the files of earlier renders", async () => {
    await rendercv.render({ yaml, design: "#let design = oops(" }).catch(() => undefined);

    const cv = await rendercv.render({ yaml }, { formats: ["typst"] });

    expect(cv.typst).not.toContain("/design.typ");
  });

  test("uses other files, like a photo", async () => {
    // The smallest valid PNG: one transparent pixel.
    const photo = Uint8Array.from(
      atob(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
      ),
      (character) => character.charCodeAt(0),
    );

    const cv = await rendercv.render(
      { yaml: yaml.replace("  email:", "  photo: images/photo.png\n  email:"), files: { "images/photo.png": photo } },
      { formats: ["typst"] },
    );

    expect(cv.typst).toContain('"/images/photo.png"');
  });

  test("applies overrides", async () => {
    const cv = await rendercv.render({ yaml, overrides: { "cv.name": "John Smith" } }, { formats: ["markdown"] });

    expect(cv.markdown).toStartWith("# John Smith");
  });

  test("throws the problems of an invalid CV", async () => {
    const invalid = `cv:
  name: Jane Doe
  sections:
    Experience:
      - compny: ACME
        position: Engineer
`;

    const error = await rendercv.render({ yaml: invalid }).catch((e: unknown) => e);

    expect(error).toBeInstanceOf(RenderCVError);
    expect((error as RenderCVError).problems).toEqual([
      {
        message: "The entry type `experience` has no field `compny`. Did you mean `company`?",
        source: "input",
        path: ["cv", "sections", "Experience", "0", "compny"],
        line: 5,
        column: 9,
        endLine: 5,
        endColumn: 16,
      },
    ]);
  });

  test("throws Typst errors with where they are", async () => {
    const error = await rendercv
      .render({ yaml, design: designFor("classic").replace("classic()", 'classic(page: (sise: "a4"))') })
      .catch((e: unknown) => e);

    expect(error).toBeInstanceOf(RenderCVError);
    const [problem] = (error as RenderCVError).problems;
    expect(problem!.message).toContain("Unknown design option `page.sise`. Did you mean `size`?");
    expect(problem!.message).toContain("`design.typ`, line 2");
    expect(problem!.path).toEqual([]);
    expect(problem!.line).toBeUndefined();
  });

  test("rejects unknown formats", async () => {
    // @ts-expect-error: "docx" isn't a format.
    await expect(rendercv.render({ yaml }, { formats: ["docx"] })).rejects.toThrow("Unknown output formats: docx.");
  });

  test.each(["../photo.png", "/etc/passwd", "C:\\photo.png", ""])("rejects the file path %p", async (path) => {
    await expect(rendercv.render({ yaml, files: { [path]: "x" } })).rejects.toThrow("should be relative to the YAML file");
  });

  test("renders one CV at a time", async () => {
    const names = ["Ada", "Grace", "Alan"];

    const cvs = await Promise.all(
      names.map((name) => rendercv.render({ yaml: yaml.replace("Jane Doe", name) }, { formats: ["markdown"] })),
    );

    expect(cvs.map((cv) => cv.markdown!.split("\n")[0])).toEqual(names.map((name) => `# ${name}`));
  });
});

describe("validate", () => {
  test("returns no problems for a valid CV", async () => {
    expect(await rendercv.validate({ yaml })).toEqual([]);
  });

  test("returns the problems of an invalid CV", async () => {
    const problems = await rendercv.validate({ yaml: "cv:\n  email: not-an-email\n" });

    expect(problems).toHaveLength(1);
    expect(problems[0]).toMatchObject({ source: "input", path: ["cv", "email"], line: 2 });
  });
});

test("reports its version", () => {
  expect(rendercv.version).toBe(version);
  expect(version).toMatch(/^\d+\.\d+\.\d+/);
});
