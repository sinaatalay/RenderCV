---
name: rendercv
description: >-
  Create professional CVs and resumes with perfect typography using RenderCV
  (v{{ version }}). Users write content in YAML, and RenderCV produces
  publication-quality PDFs via Typst typesetting. {{ available_designs | length }}
  built-in designs, customized in a small Typst file (`design.typ`): colors,
  fonts, margins, spacing, section title styles, entry layouts, and more. Custom
  entry types in `entries.typ`. Any language supported ({{ available_locales | length }}
  built-in, or define your own). Outputs PDF, PNG, HTML, and Markdown. Use when
  the user wants to create, edit, customize, or render a CV or resume.
---

## Quick Start

**Built-in designs:** `{{ available_designs | join("`, `") }}`
**Built-in locales:** `{{ available_locales | join("`, `") }}`

```bash
# Install RenderCV
uv tool install "rendercv[full]"

# Create a starter YAML file (optionally with a design.typ and an entries.typ)
rendercv new "John Doe"
rendercv new "John Doe" --design moderncv --locale german --entries

# Render to PDF (also generates Typst, Markdown, HTML, PNG by default)
rendercv render John_Doe_CV.yaml

# Watch mode: auto-re-render whenever the YAML file, design.typ, or entries.typ changes
rendercv render John_Doe_CV.yaml --watch

# Render only PNG (useful for previewing or checking page count)
rendercv render John_Doe_CV.yaml --dont-generate-pdf --dont-generate-html --dont-generate-markdown

# Override fields from the CLI without editing the YAML
rendercv render John_Doe_CV.yaml --cv.name "Jane Doe" --locale.language "german"

# Upgrade a RenderCV 2 file (moves its `design:` field into design.typ)
rendercv migrate John_Doe_CV.yaml
```

## A CV Is Up to Three Files

```
John_Doe_CV.yaml   # Content (cv), language (locale), settings. Any file name.
design.typ         # Optional: how it looks. Default: the classic design.
entries.typ        # Optional: which entry types exist. Default: the standard ones.
```

`design.typ` and `entries.typ` next to the YAML file are used automatically. Other files can be chosen with `rendercv render --design FILE.typ --entries FILE.typ` or with `settings.render_command.design` / `settings.render_command.entries` in the YAML.

**IMPORTANT: RenderCV 3 has no `design:` field in the YAML.** A YAML file with a `design:` key is an error. All visual customization goes into `design.typ`. Never write `design: theme: ...`.

## YAML Structure

```yaml
cv:         # Your content: name, contact info, and all sections
locale:     # Language: month names, "present", phrases, direction
settings:   # Behavior: output paths, bold keywords, current date, design/entries files
```

Only `cv` is required. The YAML maps to these Pydantic models (validators omitted):

```python
{{ model_sources.rendercv_model }}
```

```python
{{ model_sources.cv }}
```

```python
{{ model_sources.social_network }}
```

Available social networks: `{{ available_social_networks | join("`, `") }}`. For anything else, use `custom_connections`:

```python
{{ model_sources.custom_connection }}
```

```python
{{ model_sources.locale }}
```

```python
{{ model_sources.settings }}
{{ model_sources.render_command }}
```

## Sections and Entry Types

`cv.sections` maps section titles (any text; `snake_case` keys become Title Case) to lists of entries. A section can also be a mapping of subsection titles to lists of entries.

The entry type of each entry is detected from its fields: an entry fits a type if it has all the type's required fields and no fields the type doesn't have. An entry that is plain text is a `paragraph`. If several types fit, add `type: <name>` to the entry. **Unknown fields are errors**, so never invent fields; to add a field, declare an entry type in `entries.typ` (see below).

**Standard entry types:**

| Entry type | Required fields | Optional fields | Use |
|---|---|---|---|
{% for entry_type in entry_types %}
| `{{ entry_type.name }}` | {{ entry_type.required }} | {{ entry_type.optional }} | {{ entry_type.doc }} |
{% endfor %}

Dates: `start_date`/`end_date` take `YYYY-MM-DD`, `YYYY-MM`, or `YYYY`; `end_date` can be `present` (omitting it also means ongoing). A single `date` also accepts free text like `"Fall 2023"`. Use either `date` or `start_date`/`end_date`.

```yaml
cv:
  sections:
    experience:              # experience (company + position)
      - company: Google
        position: Engineer
        start_date: 2020-01
        highlights:
          - Did something impactful
    skills:                  # one_line (label + details)
      - label: Languages
        details: Python, C++
    about_me:                # paragraph (plain text)
      - This is a free-form paragraph about me.
    projects:
      Open source:           # subsection
        - name: FlashInfer   # normal (name)
          date: 2023
```

## Text

- All text fields support inline Markdown: `**bold**`, `*italic*`, `[link text](url)`, `` `code` ``, and `$$math$$` (Typst math syntax). Block-level Markdown (headings, lists) is not supported.
- Everything else is printed literally: `$`, `#`, `@`, `<` need no escaping.
- Raw Typst markup: tag the value with `!typst`, e.g. `- !typst "Showed that $f(x) = x^2$ is a #emph[parabola]."`
- Nested bullets in `highlights`: put ` - ` inside a bullet, or indent the sub-bullets on the next lines (YAML joins them):

    ```yaml
    highlights:
      - Main bullet point
        - Sub-bullet 1
        - Sub-bullet 2
    ```

- Publication `authors`: wrap the CV owner's name in `**double asterisks**` to bold it.

### YAML quoting

**ALWAYS quote string values that contain a colon followed by a space (`: `) or ` #`.** This is the most common cause of invalid YAML:

```yaml
# WRONG — colon breaks YAML parsing, and " #1" becomes a comment:
- title: Catalytic Mechanisms: A New Approach
  highlights:
    - Closed issue #1 in the tracker

# RIGHT — wrap in double quotes:
- title: "Catalytic Mechanisms: A New Approach"
  highlights:
    - "Closed issue #1 in the tracker"
```

### Phone numbers

Phone numbers MUST include the country code (`"+15551234567"`). Never invent a phone number — only include one if the user provides it. If the user provides a local number without country code, ask which country, or omit the phone field.

## Design (`design.typ`)

`design.typ` must define `design`. The simplest one picks a built-in design and changes options:

```typst
{{ sample_design }}
```

All built-in designs share the options below and differ only in their defaults. Options are nested Typst dictionaries that merge key by key, so only changed options are needed. Values are Typst values: lengths `0.7in`/`10pt`/`1.2em`, colors `rgb("#004f90")`/`rgb(0, 79, 144)`, alignments `left`/`center`/`right` (no quotes), text `"a4"` (quoted). A one-element array needs a trailing comma: `("experience",)`. Unknown options and wrong types are errors.

These are all options with the classic design's defaults:

```typst
{{ engine_defaults }}
```

Choices: `page.size` any Typst paper (`"us-letter"`, `"a4"`, ...); `typography.alignment` `"justified"`/`"left"`/`"justified-with-no-hyphenation"`; `typography.font_family` one font name or a dictionary per part; `header.photo_position` `"left"`/`"right"`; `header.connections.phone_number_format` `"national"`/`"international"`/`"e164"`; `section_titles.type` `"with_partial_line"`/`"with_full_line"`/`"without_line"`/`"moderncv"`/`"centered_without_line"`/`"centered_with_partial_line"`/`"centered_with_centered_partial_line"`/`"centered_with_full_line"`; `sections.show_time_spans_in` section keys (lowercase title with underscores).

Example: dark red, A4, 1-inch margins, New Computer Modern:

```typst
#import "@preview/rendercv:{{ version }}": designs

#let design = designs.classic(
  page: (size: "a4", top_margin: 1in, bottom_margin: 1in, left_margin: 1in, right_margin: 1in),
  colors: (name: rgb("#8b0000"), section_titles: rgb("#8b0000")),
  typography: (font_family: "New Computer Modern"),
)
```

To change how one entry type looks, replace its look in the design's `entries` (a design is a Typst dictionary):

```typst
#import "@preview/rendercv:{{ version }}": designs

#let base = designs.sb2nov()
#let design = base + (
  entries: base.entries + (
    one_line: (it, ctx) => block(below: 0.8em)[#smallcaps(it.label) · #it.details],
  ),
)
```

## Custom Entry Types (`entries.typ`)

`entries.typ` is a Typst module; every entry type it defines or imports is allowed in the YAML. `rendercv new "John Doe" --entries` creates this one:

```typst
{{ sample_entries }}
```

Field kinds: `markdown`, `text` (optional `pattern:`), `date` (`allow-text: true` for free text), `url`, `email`, `phone`, `number`, `bool`, `choice` (`choices: (...)`), `list` (`of: "markdown"`), `bullets`, `entries`. `field(kind, optional: true, doc: "...")`. A look `(it, ctx) => ...` returns content or hands over to another type with `as-entry("normal", ...)`, so every design draws it.

To add a field to a standard type, make a new type with the standard fields plus a **required** new field, handing over to the standard type:

```typst
#import "@preview/rendercv:{{ version }}": *

#let job = entry-type(
  fields: experience.fields + (tech_stack: field("markdown")),
  look: (it, ctx) => as-entry(
    "experience",
    company: it.company,
    position: it.position,
    date: it.date,
    start_date: it.start_date,
    end_date: it.end_date,
    location: it.location,
    summary: [_Tech stack:_ #it.tech_stack],
    highlights: it.highlights,
  ),
)
```

## Locale

Set `locale.language` to a built-in locale and override any field. For another language, give it any name and provide every field (`iso_code`, `last_updated`, `present`, `month`, `months`, `year`, `years`, `phrases.degree_with_area`, `month_abbreviations`, `month_names`; `direction` defaults to `ltr`). `phrases.degree_with_area` is Typst markup: `"#degree in #area"`.

## CLI Reference

### `rendercv new "Full Name"`

| Option | What it does |
|---|---|
| `--design NAME` | Also create a `design.typ` using this built-in design |
| `--locale LOCALE` | Locale to use (default: `english`) |
| `--entries` | Also create an `entries.typ` with an example custom entry type |

### `rendercv render <input.yaml>`

| Option | Short | What it does |
|---|---|---|
| `--watch` | `-w` | Re-render automatically when an input file changes |
| `--quiet` | `-q` | Suppress all output messages |
| `--design FILE.typ` | `-d` | Use this design file instead of `design.typ` |
| `--entries FILE.typ` | `-e` | Use this entry types file instead of `entries.typ` |
| `--locale-catalog FILE` | `-lc` | Load the `locale` field from a separate YAML file |
| `--settings FILE` | `-s` | Load the `settings` field from a separate YAML file |
| `--output-folder DIR` | `-o` | Custom output directory |

Per-format controls: `--{format}-path PATH` sets a custom output path, `--dont-generate-{format}` skips generation. Formats: `pdf`, `typst`, `markdown`, `html`, `png`. Any YAML field can be overridden with dot notation: `--cv.sections.education.0.institution "MIT"`.

### `rendercv migrate <input.yaml>`

Converts a RenderCV 2 file: moves its `design:` field into `design.typ` and keeps the original as `*.v2.yaml`.

## JSON Schema

For YAML editor autocompletion and validation (standard entry types only):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v{{ version }}/schema.json
```

## Complete Example

```yaml
{{ sample_cv }}
```
