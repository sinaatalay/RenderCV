# RenderCV for JavaScript

[RenderCV](https://rendercv.com) turns a CV written in YAML into a PDF with professional typography. This package is the same RenderCV as the command line, running in [Pyodide](https://pyodide.org) (Python compiled to WebAssembly), in Node.js, Bun, and browsers.

```sh
bun add rendercv  # or: npm install rendercv
```

```js
import { loadRenderCV } from "rendercv";

const rendercv = await loadRenderCV();

const cv = await rendercv.render(
  {
    yaml: `cv:
  name: Jane Doe
  email: jane@example.com
  sections:
    education:
      - institution: Princeton University
        area: Computer Science
        degree: PhD
        start_date: 2018-09
        end_date: 2023-05
`,
  },
  { formats: ["pdf", "markdown"] },
);
// cv.pdf is a Uint8Array, cv.markdown a string.
```

Loading takes two to four seconds, once per page or process: Pyodide starts, and RenderCV and its dependencies are installed into it. After that, a render takes a fraction of a second. Load once, render many times.

## Projects

A CV is up to three files, as with the command line: the YAML, `design.typ`, and `entries.typ`. Give them as strings:

```js
const cv = await rendercv.render({
  yaml,
  design: `#import "@preview/rendercv:3.0.0": designs
#let design = designs.moderncv(page: (size: "a4"))
`,
  entries: entriesTyp,
  // Other files, by their paths relative to the YAML file:
  files: { "photo.jpg": photoBytes, "fonts/Inter-Regular.ttf": fontBytes },
  // Like `rendercv render --cv.name "John Doe"`:
  overrides: { "cv.name": "John Doe" },
});
```

The formats are `pdf`, `png` and `svg` (one image per page), `html`, `markdown`, and `typst` (a Typst file that compiles on its own).

## Problems

`render` throws a `RenderCVError` when a CV has problems; `validate` returns them without rendering:

```js
const problems = await rendercv.validate({ yaml });
// [{ message: "The entry type `experience` has no field `compny`. Did you mean `company`?",
//    source: "input", path: ["cv", "sections", "experience", "0", "compny"],
//    line: 5, column: 9, endLine: 5, endColumn: 16 }]
```

Problems in the YAML have their line and column, for showing them in an editor. Errors in `design.typ` or `entries.typ` say where they are in their message.

## Options

```js
const rendercv = await loadRenderCV({
  // Install RenderCV's fonts (a 33 MB download, kept in the package's .cache
  // folder in Node.js and Bun), so CVs look exactly as with the command line.
  // Without them, Typst's built-in fonts are used and the designs' icons are
  // missing. Default: true.
  fonts: true,
  // Use a Pyodide your app already loaded:
  pyodide,
  // Where Pyodide's files are. Default: the `pyodide` package in Node.js and
  // Bun, the jsDelivr CDN in browsers.
  indexURL,
  // The folder with the wheels of RenderCV and its dependencies. Default: the
  // package's `wheels` folder.
  wheelsURL,
});
```

## In browsers

Pyodide runs on the thread it's loaded in, so load RenderCV in a Web Worker to keep the page responsive.

The package finds its wheels with `new URL("../wheels/", import.meta.url)`, which bundlers don't copy. Serve `node_modules/rendercv/wheels/` with your site and pass its URL as `wheelsURL`, or use jsDelivr: `wheelsURL: "https://cdn.jsdelivr.net/npm/rendercv@3.0.0/wheels/"`. With Vite, also add `rendercv` and `pyodide` to `optimizeDeps.exclude`.

## Versions

The package's version is the version of RenderCV it runs. It contains the wheels of RenderCV and its dependencies, resolved for its Pyodide version when it was built, so it always runs the versions it was tested with and doesn't download them. See the [documentation](https://docs.rendercv.com) for the YAML format, entry types, and designs.

## License

MIT
