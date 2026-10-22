# JavaScript and Python

RenderCV can render CVs from your own code: from JavaScript with the `rendercv` npm package, and from Python with `rendercv.api`. Both take the same files as the command line (the YAML, `design.typ`, `entries.typ`) and return the outputs instead of writing them.

## JavaScript

The [`rendercv` npm package](https://www.npmjs.com/package/rendercv) is the same RenderCV, running in [Pyodide](https://pyodide.org) (Python compiled to WebAssembly). It works in Node.js, Bun, and browsers.

```sh
bun add rendercv  # or: npm install rendercv
```

```js
import { loadRenderCV, RenderCVError } from "rendercv";

const rendercv = await loadRenderCV();

try {
  const cv = await rendercv.render(
    { yaml, design, entries },
    { formats: ["pdf", "png", "markdown"] },
  );
  // cv.pdf: Uint8Array, cv.png: Uint8Array[] (one per page), cv.markdown: string
} catch (error) {
  if (error instanceof RenderCVError) {
    // error.problems: [{ message, source, path, line, column, endLine, endColumn }]
  }
}
```

- `yaml` is the YAML file's content; `design` and `entries` are the contents of `design.typ` and `entries.typ`, and can be left out.
- `files` gives other files by their paths relative to the YAML file, like a photo (`"photo.jpg"`) or fonts (`"fonts/Inter-Regular.ttf"`).
- `overrides` replaces values in the YAML, like `rendercv render --cv.name "Jane Doe"`: `{ "cv.name": "Jane Doe" }`.
- The formats are `pdf`, `png`, `svg`, `html`, `markdown`, and `typst`.
- `rendercv.validate(project)` returns the problems of a CV without rendering it, with their lines and columns in the YAML, for showing them in an editor.

Loading takes two to four seconds, once per page or process: Pyodide starts, and RenderCV and its dependencies (whose wheels come in the package) are installed into it. A render then takes a fraction of a second. RenderCV's fonts (33 MB) are downloaded once; pass `{ fonts: false }` to `loadRenderCV` to skip them, and Typst's built-in fonts are used instead (the designs' icons are then missing).

In browsers, load RenderCV in a Web Worker, since Pyodide runs on the thread it's loaded in. See the [package's README](https://github.com/rendercv/rendercv/tree/main/js) for all options and for bundlers.

The npm package's version is the version of RenderCV it runs.

## Python

`rendercv.api` renders and validates CVs from files, like the command line, but returns the outputs:

```python
import pathlib

from rendercv.api import render, validate

problems = validate(pathlib.Path("John_Doe_CV.yaml"))
for problem in problems:
    print(f"Line {problem.line}: {problem.message}")

cv = render(pathlib.Path("John_Doe_CV.yaml"), formats=("pdf", "markdown"))
pathlib.Path("cv.pdf").write_bytes(cv.pdf)
```

`design.typ` and `entries.typ` next to the YAML file are used if they exist; `design_file` and `entries_file` choose others. `render` raises `RenderCVUserValidationError` or `RenderCVUserError` for invalid input; `problems_from_error` turns them into the same problems `validate` returns.
