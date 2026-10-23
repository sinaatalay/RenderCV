---
toc_depth: 2
---

# Publish the Typst Package

RenderCV's Typst library contains the layout code that turns CV content into pages. It lives in `src/rendercv/renderer/rendercv_typst/` and can also be used directly from Typst, without the Python application. [Typst Universe](https://typst.app/universe/) is the public catalog where Typst users can find and import it.

The library's version is independent of the Python package. Publishing it requires a pull request to [typst/packages](https://github.com/typst/packages); the Python release workflow does not submit that PR.

## Check the package

`typst.toml` is the package manifest: it tells Typst the package's name, version, and which file to load. Read it for the version being published, then check the package before preparing the submission:

- Required files: `lib.typ`, `typst.toml`, `README.md`, `LICENSE`, `thumbnail.png`, and `template/main.typ`.
- Manifest fields: package name, version, entry point, authors, license, and description; template path, entry point, and thumbnail.
- Version references: README imports, `template/main.typ`, and example imports must agree with the manifest.
- Changelog: the version must have an entry in `CHANGELOG.md`.
- Examples: every theme pictured in the README must have a corresponding `examples/<theme>.typ`; relative links must resolve.
- Template import: use `@preview/rendercv:<version>`, not a relative import of `lib.typ`.

Compile the template and examples locally and inspect the outputs. Resolve all failures before submitting. Check the upstream [publishing guide](https://github.com/typst/packages/blob/main/docs/publishing.md) for current submission requirements.

## Prepare the submission

Check for an existing PR for the same version before creating another. Use a clean branch from the current upstream `main` in your fork of `typst/packages`. An isolated checkout avoids disturbing other package submissions.

Create `packages/preview/rendercv/<version>/` and copy `lib.typ`, `typst.toml`, `README.md`, `LICENSE`, `thumbnail.png`, `template/`, and `examples/`. Exclude generated PDFs, `CHANGELOG.md`, and repository metadata. Check the copied package again, including its local links and template import.

## Open the pull request

Use the title `rendercv:<version>` and the current upstream PR template. State whether this is a new package or an update, summarize the changes from the previous published version, and retain contributor credits. Use the version's changelog as the source for the description. Report the PR link, submission branch, and any remaining review findings.
