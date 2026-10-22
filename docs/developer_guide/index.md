---
toc_depth: 1
---

# Setup

## Prerequisites

You need two tools to develop RenderCV:

- **[`uv`](https://docs.astral.sh/uv/)**: Package and project manager. It also handles Python installations, so you don't need to install Python separately.
- **[`just`](https://github.com/casey/just)**: Command runner. Development commands are defined in the [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile), and you need `just` to run them.

Install them by following their official installation guides:

- [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/)
- [Install `just`](https://github.com/casey/just#installation)

## Setting Up the Development Environment

1. Clone the repository:

    ```bash
    git clone --recursive https://github.com/rendercv/rendercv.git
    ```

    and change to the repository directory:

    ```bash
    cd rendercv
    ```

    > [!NOTE]
    > The `--recursive` flag clones the [rendercv-skill](https://github.com/rendercv/rendercv-skill) submodule. If you forgot it, run `git submodule update --init` inside the repo.

2. Set up the development environment (creates a virtual environment in `./.venv` with all dependencies):

    ```bash
    just sync
    ```

3. Run `just test` to verify all tests pass and everything is set up correctly.

4. Finally, activate the virtual environment in your integrated development environment (IDE). In Visual Studio Code:

    - Press `Ctrl+Shift+P`.
    - Type `Python: Select Interpreter`.
    - Select the one in `./.venv`.


That's it! You're now ready to start developing RenderCV.

!!! note
    In a source checkout, RenderCV serves its Typst package straight from the `typst/` folder, so edits to it take effect on the next render. The Typst packages it depends on (like `@preview/fontawesome`) are downloaded by Typst the first time you render, so you need an internet connection once. Installed RenderCV bundles them (see [Project Management](project_management.md#hatch_buildpy)).

## Available Commands

### Development

- `just sync`: Sync all dependencies (including extras and dev groups)
- `just format`: Format code with `black` and `ruff`
- `just check`: Run all checks (`ruff`, `ty`, `pre-commit`)
- `just lock`: Update `uv.lock` file

### Testing

- `just test`: Run tests with pytest
- `just test-coverage`: Run tests with coverage report
- `just update-testdata`: Update test data files (see [Testing](testing.md) for more details)

### Documentation

- `just build-docs`: Build documentation
- `just serve-docs`: Serve documentation locally with live reload

### Scripts

- `just update-schema`: Update JSON schema
- `just update-entry-figures`: Update entry figures for documentation
- `just update-examples`: Update the `examples/` folder and the design images in the docs
- `just update-skill`: Update the AI agent skill and `docs/llms.txt`
- `just create-executable`: Create standalone executable

### Utilities

- `just count-lines`: Count lines of Python code in the `src/` directory
