# `settings` Field

The `settings` field configures RenderCV's behavior, including input and output files, file generation, and text formatting.

```yaml
settings:
  current_date: 2025-12-03 # (1)!
  pdf_title: NAME - CV # (2)!
  bold_keywords: # (3)!
    - AWS
    - Python
  render_command:
    design: designs/my_design.typ # (4)!
    entries: my_entries.typ # (5)!
    locale: locales/german.yaml # (6)!
    output_folder: rendercv_output # (7)!
    typst_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.typ # (8)!
    pdf_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf
    markdown_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.md
    html_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.html
    png_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.png
    dont_generate_markdown: false
    dont_generate_html: false
    dont_generate_typst: false
    dont_generate_pdf: false
    dont_generate_png: false
```

1. The date used as "today": for file names with date placeholders, the "last updated" note, and how long ongoing entries (`end_date: present`) have lasted. The default, `today`, is the actual current date.
2. The title of the PDF, shown in browser tabs and PDF readers. The placeholders `NAME`, `CURRENT_DATE`, `MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `DAY`, `DAY_IN_TWO_DIGITS`, `YEAR`, and `YEAR_IN_TWO_DIGITS` are replaced.
3. These keywords are bolded wherever they appear as whole words in your CV.
4. The [design](../design.md), a Typst file. The default is `design.typ` next to the YAML file if it exists, otherwise the `classic` design.
5. The [entry types](../entry_types.md), a Typst file. The default is `entries.typ` next to the YAML file if it exists, otherwise the standard entry types.
6. A YAML file with a top-level [`locale`](locale.md) field, to keep the locale in its own file.
7. The folder all outputs go into by default. Output paths refer to it as `OUTPUT_FOLDER`.
8. Available placeholders are: `OUTPUT_FOLDER`, `NAME`, `NAME_IN_SNAKE_CASE`, `NAME_IN_LOWER_SNAKE_CASE`, `NAME_IN_UPPER_SNAKE_CASE`, `NAME_IN_KEBAB_CASE`, `NAME_IN_LOWER_KEBAB_CASE`, `NAME_IN_UPPER_KEBAB_CASE`, `MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `DAY`, `DAY_IN_TWO_DIGITS`, `YEAR`, `YEAR_IN_TWO_DIGITS`.

All paths are relative to the YAML file. Every `render_command` field has a [command-line option](../cli_reference.md#rendercv-render), and command-line options take precedence.
