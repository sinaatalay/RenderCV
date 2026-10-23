# `settings` Field

The `settings` field configures RenderCV's behavior, including output paths, file generation, and text formatting.

```yaml
settings:
  current_date: '2025-12-03' # (5)!
  render_command:
    output_folder: rendercv_output
    design: path/to/design.yaml # (1)!
    locale: path/to/locale.yaml # (2)!
    overlays: # (6)!
      - path/to/publications.yaml
    typst_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.typ # (3)!
    pdf_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf
    markdown_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.md
    html_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.html
    png_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.png
    svg_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.svg
    dont_generate_markdown: false
    dont_generate_html: false
    dont_generate_typst: false
    dont_generate_pdf: false
    dont_generate_png: false
    dont_generate_svg: false
  bold_keywords: # (4)!
    - AWS
    - Python
  sort_entries: none # (7)!
```


1. You can optionally split your YAML into multiple files. This file contains the `design` field.
2. You can optionally split your YAML into multiple files. This file contains the `locale` field.
3. Available placeholders are: `NAME`, `NAME_IN_SNAKE_CASE`, `NAME_IN_LOWER_SNAKE_CASE`, `NAME_IN_UPPER_SNAKE_CASE`, `NAME_IN_KEBAB_CASE`, `NAME_IN_LOWER_KEBAB_CASE`, `NAME_IN_UPPER_KEBAB_CASE`, `MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `YEAR`, `YEAR_IN_TWO_DIGITS`.
4. These keywords will be bolded wherever they appear in your CV text (highlights, summaries, etc.).
5. Date used for file naming (when using date placeholders), the "last updated" text in the top note, and time span calculations for ongoing events (entries with `end_date: present`)
6. Files merged over the input file, in order, after the design and locale files and before the ones given with `--overlay`. An overlay has the structure of an input file: its mappings are merged into the input's, and its other values (text and lists) replace the input's. See [Combine YAML Files](../how_to/combine_yaml_files.md).
7. The order of the entries of every section and subsection: `none` (as written), `reverse-chronological` (the most recent first), or `chronological` (the oldest first). Entries are ordered by their end dates, then their start dates, where a year or a month covers all its days, and the ones without dates come last in their written order.

All paths in YAML, including `design`, `locale`, and `overlays` references in a file passed with `--settings`, are relative to the **main input YAML file**. CLI path options are relative to the **current working directory**.

Design and locale references are selected independently: a CLI `--design` or `--locale-catalog` flag wins over a reference in the settings overlay, which wins over the main YAML reference. An omitted reference falls back to the lower-priority input; `null` clears it. Watch mode reloads the selected files and their references on each render.

Use `OUTPUT_FOLDER` in output paths to refer to `output_folder`, for example `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf`. Name and date placeholders work in file names; characters that can't be in a file name, like `/` and `:`, are replaced by `_`. Day placeholders include `DAY`, `DAY_IN_TWO_DIGITS`, and `DAY_ORDINAL`.

`dont_generate_typst: true` skips saving the Typst source file. PDF, PNG, and SVG are still generated unless separately disabled. PNG and SVG files are one per page: `NAME_CV_1.png`, `NAME_CV_2.png`, and so on. `dont_generate_markdown: true` also disables HTML.

## PDF standards

PDF standards describe requirements for different uses, rather than levels of visual quality. **PDF/UA-1** covers accessibility, including document structure and alternative text for images. **PDF/A** covers long-term archiving. Some can be combined; others conflict. For example, PDF/A-4 requires PDF 2.0, while PDF/UA-1 requires an earlier version. See [Typst's PDF standards guide](https://typst.app/docs/reference/pdf/#pdf-standards).

RenderCV requests PDF/UA-1 by default. Leave this setting unchanged for an ordinary CV. It requires `cv.name` as the document's main heading; a missing or blank name is rejected during input validation. Custom Typst images and formulas also need appropriate alternative text.

Use `pdf_standards` when a recipient requires a particular standard. For example, `[ua-1, a-2b]` also requests archival PDF/A-2b while retaining the accessibility checks. Incompatible combinations are rejected during validation.

An empty list disables the additional conformance requirements, which allows documents such as an unnamed PDF:

```yaml
settings:
  pdf_standards: []
```

This does not remove the document's structural tags, but it stops requiring PDF/UA-1 conformance.
