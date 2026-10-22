---
toc_depth: 2
---

# Design (`design.typ`)

How your CV looks is its design: a [Typst](https://typst.app) file named `design.typ` next to the YAML file. Without one, RenderCV uses the `classic` design.

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let design = designs.moderncv()
```

`rendercv new "Your Name" --design moderncv` creates this file for you. The only rule is that `design.typ` defines `design`. Everything else is plain Typst.

To use a design file with another name, pass `--design FILE.typ` to `rendercv render` or set [`settings.render_command.design`](yaml_input_structure/settings.md).

## Built-in Designs

RenderCV comes with << design_count >> designs: << available_designs >>. Switching designs is changing one word.

{$ for design in design_names $}
=== "`<< design >>`"
    ![The << design >> design](../assets/images/examples/<< design >>.png)
{$ endfor $}

## Options

All built-in designs are built on the same engine and share its options; they differ only in their defaults and in how a few entry types are arranged. Change any option by passing it to the design:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let design = designs.classic(
  page: (size: "a4", show_top_note: false),
  colors: (name: rgb("#8b0000"), section_titles: rgb("#8b0000"), links: rgb("#8b0000")),
  typography: (font_family: "New Computer Modern"),
  section_titles: (type: "with_full_line"),
  entries: (highlights: (bullet: "–")),
)
```

Options are nested dictionaries, and they merge key by key: only the options you set change. Values are Typst values:

- Lengths: `0.7in`, `1.2em`, `10pt`, `2cm`
- Colors: `rgb("#004f90")`, `rgb(0, 79, 144)`, or a named color like `blue`
- Alignments: `left`, `center`, `right` (without quotes)
- Text: `"a4"`, `"with_full_line"` (with quotes)

A misspelled option or a value of the wrong type stops rendering with an error that names it, for example: ``Unknown design option `colors.nmae`. Available options here: `body`, `name`, `headline`, ...``

### All Options

These are all options with the `classic` design's defaults, straight from the engine's source:

```typst
<< engine_defaults >>
```

- `page.size`: any [Typst paper size](https://typst.app/docs/reference/layout/page/#parameters-paper), like `"us-letter"`, `"a4"`, or `"a5"`.
- `typography.alignment`: `"justified"`, `"left"`, or `"justified-with-no-hyphenation"`.
- `typography.font_family`: one font name for everything (`font_family: "Lato"`), or a dictionary with a font for each part. The fonts that come with RenderCV are << available_font_families >>. Any font installed on your computer works too, and so do [your own font files](how_to/custom_fonts.md).
- `typography.date_and_location_column_alignment`, `header.alignment`: `left`, `center`, or `right`.
- `header.photo_position`: `"left"` or `"right"`.
- `header.connections.phone_number_format`: `"national"`, `"international"`, or `"e164"`.
- `section_titles.type`: `"with_partial_line"`, `"with_full_line"`, `"without_line"`, `"moderncv"`, `"centered_without_line"`, `"centered_with_partial_line"`, `"centered_with_centered_partial_line"`, or `"centered_with_full_line"`.
- `sections.show_time_spans_in`: the sections whose entries show how long they lasted ("2 years 3 months"), by their key: the section title in lowercase with underscores, like `("experience", "work_history")`.
- `entries.highlights.bullet`, `entries.highlights.nested_bullet`: any text.

### Each Design's Defaults

The other designs change these defaults:

{$ for design, source in design_defaults.items() $}
=== "`<< design >>`"

    ```typst
<< source | indent(4, first=True) >>
    ```
{$ endfor $}

### Templates

The `templates` option holds small Typst functions for the parts of the CV that are text rather than layout:

| Template      | Arguments           | Writes                                                  |
| ------------- | ------------------- | ------------------------------------------------------- |
| `footer`      | `info`              | The footer of every page                                |
| `top_note`    | `info`              | The note at the top of the first page                   |
| `single_date` | `date, locale`      | A date with a month, like "Sept 2023"                   |
| `date_range`  | `start, end`        | A date range from two written dates                     |
| `time_span`   | `start, end, ctx`   | How long something lasted, like "2 years 3 months"      |

`info` has the CV owner's `name`, the `locale`, the `current-date`, and `format-date` (a function that writes a date with `single_date`). A date has `year`, `month`, `day`, `present` (`true` for "present"), and `text` (for dates like "Fall 2023").

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let design = designs.classic(
  templates: (
    footer: info => [#info.name -- Curriculum Vitae],
    top_note: info => none,
    single_date: (date, locale) => [#locale.month_names.at(date.month - 1) #date.year],
    date_range: (start, end) => [#start to #end],
  ),
)
```

## Changing How Entries Look

A design can restyle any entry type, including [your own](entry_types.md#your-own-entry-types). The design's `entries` dictionary maps entry type names to looks: functions that draw one entry. See [Change How an Entry Type Looks](how_to/change_how_an_entry_type_looks.md) for a step-by-step guide.

Every built-in design comes with the building blocks of its own looks in `parts`, so restyled entries keep the design's columns and spacing:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let base = designs.classic(colors: (name: rgb("#8b0000")))
#let (regular-entry, entry-dates, entry-body, ..) = base.parts
#let design = base + (
  entries: base.entries + (
    // Position first, then the company:
    experience: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.position) at #it.company],
      (it.location, ..entry-dates(it, ctx)),
      body: entry-body(it, ctx),
    ),
  ),
)
```

To build a design of your own on the same engine, call `designs.engine(options, entries: (o, parts) => (...))`, where `entries` returns looks built from the same parts. `designs.resolve-options(defaults, options)` merges your options into the engine's defaults; the first argument holds a design's own defaults (`(:)` for classic). `o` is the resolved options, and `parts` holds:

| Part                                                   | What it draws                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `regular-entry(ctx, main, aside, body: none, degree: none)` | An entry with a main column (`main`) and a date and location column (`aside`), each a line or an array of lines, with `body` below |
| `text-entry(ctx, content)`                             | A one-line, bullet, numbered, or paragraph entry                                           |
| `entry-dates(it, ctx)`                                 | The entry's dates as an array of lines, with its time span if its section shows them      |
| `entry-body(it, ctx)`                                  | The entry's `summary` and `highlights`                                                    |
| `summary-block(summary, ctx)`                          | A summary, spaced like the design's summaries                                             |
| `degree-with-area(it, ctx)`                            | "PhD in Computer Science", with the locale's phrase                                       |
| `publication-link(it)`                                 | A publication's DOI link, or else its URL                                                 |
| `dash-location(location)`                              | " -- Location", if there is a location                                                    |
| `lines(..items)`                                       | The items that are not empty                                                               |

## Writing a Design from Scratch

A design is a Typst dictionary. Every key is optional; whatever a design leaves out is drawn in plain, semantic Typst:

| Key        | Value                                   | What it does                                                                      |
| ---------- | --------------------------------------- | --------------------------------------------------------------------------------- |
| `document` | `(body, info) => content`               | Sets up the page, fonts, and headings, and wraps the whole CV                     |
| `layout`   | `(header, sections, ctx) => content`    | Arranges the header and the sections (each has `key`, `title`, and `body`)        |
| `header`   | `(header, ctx) => content`              | Draws the name, headline, photo, and connections                                 |
| `section`  | `(section, body, ctx) => content`       | Draws a section's title and its entries (`section.level` is 2 for subsections)   |
| `entries`  | entry type names to `(it, ctx) => content` | Draws entries of those types; other types use their own looks                  |

The CV's name is a level 1 heading and section titles are level 2 headings, so `show heading` rules style them:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": format-dates, bullet-list

#let design = (
  document: (body, info) => {
    set document(title: info.title, author: info.author)
    set page(paper: "a4", margin: 2cm)
    set text(font: "Lato", size: 10pt, lang: info.locale.iso_code)
    show heading.where(level: 1): set text(size: 24pt)
    show heading.where(level: 2): it => block(above: 1.2em, below: 0.6em, smallcaps(it.body))
    body
  },
  entries: (
    normal: (it, ctx) => block(below: 1em)[
      *#it.name* #h(1fr) #format-dates(ctx.locale, date: it.date, start: it.start_date, end: it.end_date)

      #if it.summary != none { it.summary }
      #bullet-list(it.highlights)
    ],
  ),
)
```

This design only draws `normal` entries itself, yet `experience`, `education`, and `publication` entries look right too: their own looks hand them over to `normal` (see [how looks work](entry_types.md#looks)).

A design can also start from a built-in one and replace parts of it, since designs are dictionaries: `designs.sb2nov() + (section: (section, body, ctx) => ...)`.
