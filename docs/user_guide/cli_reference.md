---
toc_depth: 1
---

# CLI Reference

RenderCV provides a command-line interface with three commands:

- **`rendercv new`** - Generate a sample CV to get started
- **`rendercv render`** - Generate PDF, Typst, Markdown, HTML, and PNG files from your YAML input
- **`rendercv migrate`** - Convert a RenderCV 2 YAML file to RenderCV 3

!!! tip "New to command line?"
    Commands are typed in your terminal/command prompt. Options starting with `--` modify behavior:

    ```bash
    rendercv new "John Doe" --design moderncv
    ```

    **You can combine multiple options** in a single command:

    ```bash
    rendercv render CV.yaml --watch --dont-generate-html --dont-generate-png
    ```

    This renders your CV with auto-reload enabled, skipping HTML and PNG generation.

## `rendercv`

Check your installed version:

```bash
rendercv --version
```

Get help anytime:

```bash
rendercv --help
rendercv render --help
```

## `rendercv new`

Generate a sample CV file to start editing.

**Basic usage:**

```bash
rendercv new "John Doe"
```

This creates `John_Doe_CV.yaml` in your current folder. Files that already exist are never overwritten.

### All Options

| Option            | What it does                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| `--design NAME`   | Also create a `design.typ` that uses this built-in design, to change its options or replace it   |
| `--locale NAME`   | The language of the CV (default: `english`)                                                       |
| `--entries`       | Also create an `entries.typ` with the standard entry types and an example of your own entry type |

Available designs: << available_designs >>

Available locales: << available_locales >>

**Example:**

```bash
rendercv new "John Doe" --design moderncv --locale french --entries
```

creates `John_Doe_CV.yaml`, `design.typ`, and `entries.typ`. See [Design](design.md) and [Entry Types](entry_types.md) for what to do with them.

## `rendercv render`

Generate your CV outputs (PDF, Typst, Markdown, HTML, PNG) from a YAML file.

**Basic usage:**

```bash
rendercv render John_Doe_CV.yaml
```

This creates a `rendercv_output` folder with all formats. If `design.typ` or `entries.typ` exist next to the YAML file, they are used.

### Common Scenarios

**Auto-reload while editing:**

```bash
rendercv render John_Doe_CV.yaml --watch
```

The CV regenerates automatically whenever you save the YAML file, `design.typ`, `entries.typ`, or the locale and settings files it uses. Great for live preview!

**Only generate PDF:**

```bash
rendercv render John_Doe_CV.yaml --dont-generate-markdown --dont-generate-html --dont-generate-png
```

Or use the short form:

```bash
rendercv render John_Doe_CV.yaml -nomd -nohtml -nopng
```

**Try another design without touching your files:**

```bash
rendercv render John_Doe_CV.yaml --design other_design.typ
```

**Custom output location:**

```bash
rendercv render John_Doe_CV.yaml --pdf-path ~/Desktop/MyCV.pdf
```

### All Options

| Option                     | Short     | What it does                                                         |
| -------------------------- | --------- | -------------------------------------------------------------------- |
| `--watch`                  | `-w`      | Re-render when any input file changes                                |
| `--quiet`                  | `-q`      | Hide all messages                                                    |
| `--design FILE`            | `-d`      | Use this Typst file as the design instead of `design.typ`           |
| `--entries FILE`           | `-e`      | Use this Typst file as the entry types instead of `entries.typ`     |
| `--locale-catalog FILE`    | `-lc`     | Load the `locale` field from a separate YAML file                    |
| `--settings FILE`          | `-s`      | Load the `settings` field from a separate YAML file                  |
| `--output-folder FOLDER`   | `-o`      | Output folder instead of `rendercv_output`                           |
| `--pdf-path PATH`          | `-pdf`    | Custom PDF location                                                  |
| `--typst-path PATH`        | `-typ`    | Custom Typst location                                                |
| `--markdown-path PATH`     | `-md`     | Custom Markdown location                                             |
| `--html-path PATH`         | `-html`   | Custom HTML location                                                 |
| `--png-path PATH`          | `-png`    | Custom PNG location                                                  |
| `--dont-generate-pdf`      | `-nopdf`  | Skip PDF generation                                                  |
| `--dont-generate-typst`    | `-notyp`  | Skip writing the Typst file (PDF and PNG are still generated)       |
| `--dont-generate-markdown` | `-nomd`   | Skip Markdown generation                                             |
| `--dont-generate-html`     | `-nohtml` | Skip HTML generation                                                 |
| `--dont-generate-png`      | `-nopng`  | Skip PNG generation                                                  |

`--design` and `--entries` paths are relative to the current folder. The output paths are relative to the YAML file. The same settings can be written in the YAML file's [`settings`](yaml_input_structure/settings.md) field; command-line options take precedence.

**Override any YAML value:**

Use dot notation to change specific fields. This overrides values in the YAML without editing the file.

```bash
rendercv render CV.yaml --cv.phone "+1-555-555-5555"
rendercv render CV.yaml --cv.sections.education.0.institution "MIT"
rendercv render CV.yaml --locale.language "german"
```

## `rendercv migrate`

Convert a RenderCV 2 YAML file to RenderCV 3.

```bash
rendercv migrate John_Doe_CV.yaml
```

This:

- creates `design.typ` next to the YAML file from its `design` field (or from the design YAML file its `settings.render_command.design` points to),
- removes the `design` field from the YAML file,
- keeps the original file as `John_Doe_CV.v2.yaml`,
- lists anything it couldn't convert.

It stops without changing anything if `design.typ` already exists. See [Migrating from RenderCV 2](migrating_from_v2.md) for details.
