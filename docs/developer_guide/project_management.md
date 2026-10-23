---
toc_depth: 2
---

# Project Management

The Python files describe what RenderCV does. The files around them describe how to install, check, and distribute it. They answer two practical questions: how can contributors use a consistent set of tools, and how can users install the result?

## Describing a Python package

[`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml) is the project's configuration file. It records the package name and version, supported Python versions, dependencies, build settings, and development-tool settings. A **dependency** is another package that our code needs, such as Pydantic for validation.

It also connects the terminal command to Python code:

```toml
[project.scripts]
rendercv = "rendercv.cli.entry_point:entry_point"
```

When RenderCV is installed, the installer creates a `rendercv` command that calls `entry_point()` in that module. This mapping is called an **entry point**.

The base `rendercv` package provides models and templating. Installing `rendercv[full]` also requests the command-line tools, Typst compiler, file watching, and fonts. Python packaging calls a named set of optional dependencies an **extra**; here its name is `full`. The smaller installation lets other applications use the Python code without installing the complete command-line application.

Development **dependency groups** serve a different purpose: they install tools for working on this repository, such as pytest or Zensical. Users do not need those tools to render a CV.

## Keeping dependencies consistent

A requirement such as `pydantic>=2.14.1` allows several versions. Installing it on different days could produce different environments. [`uv.lock`](https://github.com/rendercv/rendercv/blob/main/uv.lock) records the exact versions selected for the project, including dependencies of dependencies.

`just sync` installs from that lock file into the project's `.venv`. Commit the lock file so other contributors and automated checks use the same selections. It accounts for different platforms and Python versions; it does not make those environments identical. We still test on each supported platform. See [uv's project-file documentation](https://docs.astral.sh/uv/concepts/projects/layout/).

After changing dependencies in `pyproject.toml`, run `just lock` to update the lock file. To deliberately upgrade existing locked versions, use `uv lock --upgrade` and review and test the changes. Let uv write `uv.lock`; do not edit its resolved entries by hand.

A **workspace** groups related Python projects under one lock file and development environment. RenderCV's workspace contains the main package, `packages/rendercv-fonts`, and the ATS analysis tools. The fonts package has its own version. During development, the workspace uses its local source; an installation from PyPI uses the published package.

## Sharing development commands

[`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile) gives names to commands, so everyone can run `just test` or `just build-docs` with the same options. Run `just --list` to see them. Larger tasks, such as generating examples, live in Python files under `scripts/`; a recipe can call one of those scripts.

[`prek`](https://prek.j178.dev/) runs the checks listed in `.pre-commit-config.yaml`. A **linter** looks for code problems; a **formatter** applies consistent layout. Ruff does both. The type checker, ty, checks whether code uses values consistently with their type annotations. `just check` runs these checks and checks spelling and configuration files. The [GitHub workflows](github_workflows.md) run them on proposed changes too.

## Building distributions

A **distribution** is a file prepared for installation. A wheel (`.whl`) contains the installable package; a source distribution (`.tar.gz`) contains source from which a wheel can be built. `uv_build` is the **build backend**: the tool uv calls to create these files using the configuration in `pyproject.toml`.

From the repository root, build both RenderCV and its fonts package with:

```bash
just download-typst-packages
uv build --all-packages
```

The first command downloads the Typst packages imported by RenderCV's layout library. They are ignored by Git but included in the distributions, so built-in layouts work without downloading them when a user renders a CV. Custom Typst code can still introduce new package imports that need network access.

The build writes distributions to `dist/`. The release workflow publishes them to **PyPI**, the package index used by `pip install`. A standalone executable is another delivery format: `just create-executable` uses PyInstaller to bundle Python and the application so the user can run it without installing Python. That recipe, the release workflow, and the Dockerfile already download the Typst packages before building.
