# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is RenderCV?

RenderCV is a resume/CV builder for academics and engineers. Users write the content of their CV in YAML, and RenderCV produces PDFs with professional typography via Typst. A CV project is up to three files: the YAML (`cv`, `locale`, `settings`), an optional `entries.typ` (which entry types exist and how they look), and an optional `design.typ` (how everything looks, e.g. `designs.classic(...)`). Deployed at rendercv.com as a web app.

## Core Pipeline

```
YAML → (ruamel.yaml) → dict → (pydantic models built from entries.typ declarations) → RenderCVModel
     → data contract (JSON) → (typst-py: in-memory main.typ + typst/ package) → PDF / PNG / HTML
                                                              (typst query) → Markdown
```

1. **Parse**: `ruamel.yaml` reads the YAML (plus locale/settings overlays and CLI overrides) into a dict (`schema/yaml_reader.py`, `schema/rendercv_model_builder.py`). `!typst` tags become `TypstString`.
2. **Declarations**: Typst is queried for `declarations(types)` of the project's entry types (`renderer/typst_compiler.py`), parsed into `EntryTypeDeclaration`s (`schema/models/cv/entry_types.py`).
3. **Validate**: a pydantic model is built per entry type at runtime; `RenderCVModel` validates `cv`, `locale`, `settings` (`schema/models/`). Errors carry YAML line/column (`schema/pydantic_error_handling.py`).
4. **Data contract**: the model becomes plain JSON (`renderer/document.py`); Markdown text becomes rich-text nodes via markdown-it-py (`renderer/rich_text.py`). No Typst code is ever generated from user text.
5. **Compile**: a small in-memory `main.typ` imports `@preview/rendercv`, `entries.typ`, `design.typ`, reads the JSON from `sys.inputs`, and calls `rendercv.render(...)` (`renderer/typst_compiler.py`, `renderer/outputs.py`). HTML uses Typst's HTML export; Markdown walks the rendered Typst content (`typst/src/markdown.typ`).

## Commands

```bash
just sync              # Install dependencies
just test              # Run tests (parallel via pytest-xdist)
just check             # Lint (ruff) + type-check (ty) + pre-commit hooks
just format            # Format (black + ruff)
just update-testdata   # Regenerate reference files for tests
just test-coverage     # Run tests with coverage report
just update-schema     # Regenerate JSON schema
just update-examples   # Regenerate examples/ and the design gallery images
just update-skill      # Regenerate the AI agent skill and docs/llms.txt
just build-docs        # Build the docs (mkdocs, strict)
just build-js          # Build the npm package in js/ (resolves and bundles the wheels; syncs its version)
just test-js           # Type-check and test the npm package with Bun
```

Run a single test:
```bash
uv run --frozen --all-extras pytest tests/schema/models/cv/test_section.py -x
```

Run tests matching a keyword:
```bash
uv run --frozen --all-extras pytest -k "test_validate_sections" -x
```

## Source Layout

```
js/                             # The npm package `rendercv`: RenderCV in Pyodide (TypeScript, Bun; bundles the wheels)
typst/                          # The Typst package @preview/rendercv (bundled into the wheel by hatch_build.py)
  lib.typ                       # Public API: entry-type, field, as-entry, render, designs, standard types, ...
  src/                          # entry-type.typ, render.typ, rich.typ, dates.typ, values.typ, options.typ, markdown.typ
  entries/standard.typ          # The standard entry types (normal, experience, education, ...)
  designs/                      # engine.typ (classic engine + option defaults) and the built-in designs
src/rendercv/
  api.py                        # render()/validate() from code, returning outputs; used by the npm package
  cli/                          # Typer CLI: render, new, migrate (one folder per command)
  schema/                       # YAML reading, validation, JSON schema, samples, v2 migration
    models/
      cv/                       # Header, sections, entry types (declarations → pydantic), social networks
      locale/                   # Locale model (built-ins from data/locales)
      settings/                 # Settings and render_command
      rendercv_model.py         # Top-level RenderCVModel (cv, locale, settings)
    rendercv_model_builder.py   # YAML + overlays + overrides → RenderCVModel
  renderer/                     # Data contract, Typst compilation, outputs
    document.py                 # RenderCVModel → data contract JSON
    typst_compiler.py           # main.typ, compile, query, Typst errors
    project.py                  # load_project: find entries.typ/design.typ, validate, build data
    outputs.py                  # Typst/PDF/PNG/SVG/Markdown/HTML outputs, built or written to files
  data/
    locales/*.yaml              # Built-in locales
    social_networks/*.yaml      # Social networks (URL template, icon, username rules)
```

## Testing

Tests mirror the source structure: `src/rendercv/schema/models/cv/entry_types.py` → `tests/schema/models/cv/test_entry_types.py`. Tests of the Typst package in `tests/typst/` mirror `typst/`. `tests/test_tests.py` enforces the mirroring. The npm package has its own Bun tests in `js/tests/` (`just test-js`).

**Reference file testing**: Some tests compare generated output against reference files in `testdata` folders. Use `just update-testdata` to regenerate references when output intentionally changes, and check them before committing.

**Key fixtures** (in `tests/conftest.py`): `testdata_dir`, `update_testdata`.

## Code Conventions

- **No private API syntax**: Never use underscore-prefixed names (`_Foo`, `_bar`). All names are public.
- **Strict typing**: Every function, variable, and class attribute must have type annotations.
- **Python 3.12+ syntax**: Use `type` statements for aliases, `X | Y` unions, `X | None` for optionals.
- **Docstrings**: Google-style with Why/Args/Returns/Raises sections.
- **Pure data in YAML, behavior and looks in Typst**: locales and social networks are YAML files in `src/rendercv/data/`; entry types and designs are Typst in `typst/`.
- **`just check` must show zero errors** before committing.
- Use `uv`, never `pip` or `python` directly; use `bun`, never `npm`, for the npm package in `js/`.
