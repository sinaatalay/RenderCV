# Get Started

## Installation

1. Install [Python](https://www.python.org/downloads/) (3.12 or newer).

2. Run the command below to install RenderCV.

    === "pip"

        ```
        pip install "rendercv[full]"
        ```

    === "pipx"

        ```
        pipx install "rendercv[full]"
        ```

    === "uv"

        ```
        uv tool install "rendercv[full]"
        ```

    === "Docker"

        Docker image is available at [ghcr.io/rendercv/rendercv](https://github.com/rendercv/rendercv/pkgs/container/rendercv).

        ```bash
        docker run --rm -v "$PWD":/work -u $(id -u):$(id -g) -e HOME=/tmp -w /work ghcr.io/rendercv/rendercv new "Your Name"
        ```

## Quick Start

1. Create a new CV YAML input file

    ```bash
    rendercv new "Your Name"
    ```

    This creates a YAML input file called `Your_Name_CV.yaml` with a sample CV. It holds your content (`cv`), the language of the CV (`locale`), and RenderCV's settings (`settings`). See [YAML Input Structure](yaml_input_structure/index.md) for the full reference.

    See the [CLI Reference](cli_reference.md#rendercv-new) for the complete list of options available for the `new` command.

    !!! tip
        To start with another language or design, use the `--locale` and `--design` options:

        ```bash
        rendercv new "Your Name" --locale turkish --design engineeringresumes
        ```

        `--design` also creates a `design.typ` next to the YAML file, where you can change the design's options. See [Design](design.md).

2. Render the YAML input file with

    ```bash
    rendercv render "Your_Name_CV.yaml"
    ```

    This generates a `rendercv_output/` directory containing:

    - `Your_Name_CV.pdf`: Your CV as PDF
    - `Your_Name_CV.typ`: [Typst](https://typst.app) source code of the PDF
    - `Your_Name_CV_1.png`, `..._2.png`, ...: PNG images of each page of the PDF
    - `Your_Name_CV.md`: Your CV as Markdown
    - `Your_Name_CV.html`: Your CV as HTML

    See the [CLI Reference](cli_reference.md#rendercv-render) for the complete list of options available for the `render` command.

    !!! tip
        To re-render automatically whenever you save changes, use the `--watch` option:

        ```bash
        rendercv render --watch "Your_Name_CV.yaml"
        ```

## A CV Is Up to Three Files

The YAML file alone is a complete CV. Two optional [Typst](https://typst.app) files next to it change what it can hold and how it looks:

```
Your_Name_CV.yaml   # What your CV says: cv, locale, settings
design.typ          # Optional: how it looks
entries.typ         # Optional: which entry types exist
```

- [`design.typ`](design.md) picks one of the << design_count >> built-in designs and changes any of its options, or restyles any part of the CV.
- [`entries.typ`](entry_types.md) adds your own entry types, like a talk or a grant, next to the standard ones.

RenderCV uses them automatically when they are next to the YAML file. Delete them to go back to the built-in ones.

!!! note "Coming from RenderCV 2?"
    Run `rendercv migrate Your_Name_CV.yaml`. It moves your `design` field into a `design.typ`. See [Migrating from RenderCV 2](migrating_from_v2.md).
