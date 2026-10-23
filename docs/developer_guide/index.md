---
toc_depth: 1
---

# Setup

This guide introduces the tools used to develop RenderCV and explains how they work together. Start here to run the project, then follow [Understanding RenderCV](understanding_rendercv.md) to trace a CV from YAML to PDF.

## Prerequisites

You need three tools:

- **[Git](https://git-scm.com/)** downloads the repository and tracks changes to its files.
- **[`uv`](https://docs.astral.sh/uv/)** installs Python and the packages RenderCV depends on, including development tools. You don't need to install Python separately.
- **[`just`](https://github.com/casey/just)** runs named commands from the [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile). For example, `just test` runs the project's test command without requiring you to remember its options.

Install them by following their official installation guides:

- [Install Git](https://git-scm.com/install/)
- [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/)
- [Install `just`](https://github.com/casey/just#installation)

## Setting Up the Development Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/rendercv/rendercv.git
    ```

    and change to the repository directory:

    ```bash
    cd rendercv
    ```

2. Install the project's dependencies:

    ```bash
    just sync
    ```

    This creates a **virtual environment** in `.venv`: a Python installation and package directory for this project. Keeping them separate from other projects prevents their package versions from interfering. `uv.lock` records the versions to install; see [Project Management](project_management.md).

3. Run `just test` to verify all tests pass and everything is set up correctly.

4. Tell your editor to use this environment so it can find the installed packages. In Visual Studio Code:

    - Press `Ctrl+Shift+P`.
    - Type `Python: Select Interpreter`.
    - Select the one in `./.venv`.


Run development commands from the repository directory. The `just` recipes use `uv run` to select `.venv` automatically; you do not need to activate it in your terminal.

## Available Commands

### Development

- `just sync`: Install the locked dependencies for running and developing RenderCV
- `just format`: Format code with `ruff`
- `just check`: Check formatting, code, types, spelling, and configuration
- `just lock`: Update `uv.lock` file

### Testing

- `just test`: Run tests with pytest
- `just test-coverage`: Run tests with coverage report
- `just update-testdata`: Update test data files (see [Testing](testing.md) for more details)

### Documentation

- `just build-docs`: Build documentation
- `just serve-docs`: Serve documentation locally with live reload

### Scripts

- `just update-schema`: Update the JSON Schema used by YAML editors
- `just update-entry-figures`: Update entry figures for documentation
- `just update-examples`: Update example files
- `just update-skill`: Update the published AI agent instructions from their source
- `just create-executable`: Create standalone executable

### Utilities

- `just count-lines`: Count lines of Python code in the `src/` directory
