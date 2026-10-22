---
toc_depth: 2
---

# Entry Types (`entries.typ`)

Every entry in a section has an entry type. An entry type says which fields an entry has and how it looks. RenderCV validates each entry against its type's fields, and draws it with its type's look, restyled by the [design](design.md).

RenderCV comes with << entry_type_count >> standard entry types. An optional `entries.typ` next to the YAML file adds [your own](#your-own-entry-types).

## Standard Entry Types

You never write an entry's type: RenderCV picks the type whose fields fit the entry (see [How an Entry Finds Its Type](#how-an-entry-finds-its-type)). The standard entry types are:
{$ for name in entry_types $}
- [`<< name >>`](#<< name >>)
{$- endfor $}

Dates are written as `YYYY-MM-DD`, `YYYY-MM`, or `YYYY`. `end_date` can also be `present`, and leaving it out means the same. A single `date` can be free text too, like `Fall 2023`.

{$ for name, entry_type in entry_types.items() $}
### `<< name >>`

<< entry_type.doc >>

<< entry_type.fields_table >>

```yaml
<< entry_type.yaml >>
```

{$ for figure in entry_type.figures $}
=== "`<< figure.design >>`"
    ![<< name >> entry in the << figure.design >> design](<< figure.path >>)
{$ endfor $}

{$ endfor $}

## Your Own Entry Types

Create an `entries.typ` next to your YAML file (or run `rendercv new "Your Name" --entries`). It is a [Typst](https://typst.app) module, and every entry type it defines or imports is an entry type your YAML file can use. This one imports all standard entry types and adds a talk:

```typst title="entries.typ"
<< sample_entries_file >>
```

Now the YAML file can have talks:

```yaml
cv:
  sections:
    talks:
      - title: Scaling Laws for Efficient Inference
        event: Stanford HAI Symposium
        date: 2024-05
        slides: https://example.com/slides.pdf
```

Talks are validated like any other entry: a missing `event` or a misspelled `slides` is an error pointing to the line.

To use an entries file with another name, pass `--entries FILE.typ` to `rendercv render` or set [`settings.render_command.entries`](yaml_input_structure/settings.md).

### Fields

`entry-type(fields: ...)` maps field names to `field(kind, ...)` declarations:

```typst
field(
  "date",             // The kind, see below.
  optional: true,     // Whether the field may be left out. Default: false.
  doc: "When it was", // What the field is for. Shown in errors and editors.
  allow-text: true,   // For dates: also accept free text like "Fall 2023".
)
```

| Kind       | The YAML value                                                                  | The look receives                                                  |
| ---------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `markdown` | Text with [Markdown](yaml_input_structure/cv.md#markdown)                       | Content                                                            |
| `text`     | Plain text; with `pattern:`, it must match that regular expression              | A string                                                           |
| `date`     | `YYYY-MM-DD`, `YYYY-MM`, `YYYY`, or `present` (and any text with `allow-text: true`) | A dictionary: `year`, `month`, `day`, `present`, `text`       |
| `url`      | A URL                                                                           | A string                                                           |
| `email`    | An email address                                                                | A string                                                           |
| `phone`    | A phone number with its country code                                            | A dictionary: `e164`, `international`, `national`, `uri`          |
| `number`   | A number                                                                        | A number                                                           |
| `bool`     | `true` or `false`                                                               | A boolean                                                          |
| `choice`   | One of `choices: ("a", "b")`                                                    | A string                                                           |
| `list`     | A list of values of the kind `of: "markdown"`                                   | An array                                                           |
| `bullets`  | A list of Markdown bullets, where ` - ` starts nested bullets                   | An array of `(body, children)`; draw it with `bullet-list(...)`    |
| `entries`  | A list of entries of any entry type                                             | An array; draw it with `(ctx.render-entries)(...)`                 |

A field named `type` is not allowed: that key chooses an entry's type in the YAML.

### Looks

`look: (it, ctx) => ...` draws one entry. `it` holds the entry's fields, with `none` for optional fields that were left out. `ctx` says where the entry is:

| `ctx` key        | What it holds                                                                     |
| ---------------- | --------------------------------------------------------------------------------- |
| `locale`         | The [locale](yaml_input_structure/locale.md): `present`, `month_names`, `phrases`, ... |
| `current-date`   | The date "present" stands for                                                     |
| `settings`       | Some of the YAML's settings, like `bold_keywords`                                 |
| `section`        | The section: `key`, `title`, `level` (1, or 2 in a subsection), and `parent`      |
| `index`, `count` | The entry's position in its section (from 1), and how many entries there are     |
| `type`           | The name of the entry type being drawn                                            |
| `render-entries` | A function that draws a list of entries, for `entries` fields                     |

A look returns Typst content, or hands the entry over to another entry type with `as-entry(type, ..fields)`. A hand-over is drawn as that type, with the active design's look for it. That's why the talk above looks right in every design: it is drawn as a `normal` entry, and every design styles `normal` entries. Most standard types work the same way: `experience`, `education`, and `publication` hand over to `normal` unless the design has a look of its own for them.

A look can also return content directly, which every design then shows as it is:

```typst title="entries.typ"
#import "@preview/rendercv:3.0.0": *

// A company with several roles, each an entry of its own.
#let company = entry-type(
  doc: "A company with several roles.",
  fields: (
    company: field("markdown"),
    roles: field("entries", doc: "The roles, as entries."),
  ),
  look: (it, ctx) => {
    block(below: 0.4em, strong(it.company))
    (ctx.render-entries)(it.roles)
  },
)
```

```yaml
experience:
  - company: Acme
    roles:
      - name: Staff Engineer
        start_date: 2022-01
      - name: Engineer
        start_date: 2020-01
        end_date: 2021-12
```

Designs can give your entry types their own looks too; see [Changing How Entries Look](design.md#changing-how-entries-look).

The package has helpers for looks: `format-date(date, locale)`, `format-dates(locale, date:, start:, end:)`, `format-time-span(start, end, locale, current-date)`, `bullet-list(bullets)`, and `rich(text)`.

### Choosing and Renaming Entry Types

`entries.typ` decides the whole vocabulary. Import only the standard types you want, and rename them with `as`:

```typst title="entries.typ"
// Only these entry types, and `experience` is called `position` here:
#import "@preview/rendercv:3.0.0": education, one_line, paragraph, experience as position
```

With this file, an entry with only a `name` is an error, because there is no `normal` entry type anymore.

To add a field to a standard entry type, see [Add Fields to Entries](how_to/add_fields_to_entries.md).

## How an Entry Finds Its Type

An entry fits an entry type if it has all of the type's required fields and no fields the type doesn't have. An entry that is just text is a `paragraph`.

- If exactly one type fits, that's the entry's type.
- If several types fit, RenderCV asks you to choose one with the `type` key:

    ```yaml
    awards:
      - type: award
        name: Best Paper
        date: 2021
    ```

- If no type fits, RenderCV reports what's wrong compared to the closest type, like ``The entry type `experience` has no field `positon`. Did you mean `position`?``
