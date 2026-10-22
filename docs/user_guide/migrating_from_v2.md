# Migrating from RenderCV 2

RenderCV 3 keeps your content, but moves the design out of the YAML file. In RenderCV 2, one YAML file held `cv`, `design`, `locale`, and `settings`. In RenderCV 3, the YAML file holds `cv`, `locale`, and `settings`, and the design is a Typst file, `design.typ`, next to it.

Most CVs need one command.

## 1. Run `rendercv migrate`

```bash
rendercv migrate John_Doe_CV.yaml
```

This creates `design.typ` from the `design` field, removes the field from the YAML file, and keeps the original as `John_Doe_CV.v2.yaml`. If `settings.render_command.design` pointed to a separate design YAML file, that file's design is used.

For example, this RenderCV 2 design:

```yaml
design:
  theme: moderncv
  page:
    size: a4
    show_top_note: false
  colors:
    name: rgb(139, 0, 0)
    section_titles: '#8b0000'
  typography:
    font_family: Source Sans 3
  templates:
    single_date: MONTH_NAME YEAR
```

becomes this `design.typ`:

```typst title="design.typ"
// Converted from a RenderCV 2 `design` field by `rendercv migrate`.
#import "@preview/rendercv:3.0.0": designs

#let design = designs.moderncv(
  page: (size: "a4", show_top_note: false),
  colors: (name: rgb(139, 0, 0), section_titles: rgb("#8b0000")),
  typography: (font_family: "Source Sans 3"),
  templates: (single_date: (date, locale) => [#locale.month_names.at(date.month - 1); #date.year;]),
)
```

The design options have the same names as before, so most designs convert exactly. Then render as usual:

```bash
rendercv render John_Doe_CV.yaml
```

## 2. Convert What `migrate` Couldn't

`rendercv migrate` lists what it couldn't convert. These are the RenderCV 2 features that work differently now:

| RenderCV 2                                                        | RenderCV 3                                                                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `design.theme: moderncv`                                          | `#let design = designs.moderncv()` in `design.typ`                                                    |
| `design.templates.experience_entry.main_column` and other entry templates | A look for the entry type in `design.typ`: [Change How an Entry Type Looks](how_to/change_how_an_entry_type_looks.md) |
| `design.templates.footer: '*NAME -- PAGE_NUMBER/TOTAL_PAGES*'`    | `templates: (footer: info => context emph[#info.name -- #here().page()/#counter(page).final().first()])` (see [Templates](design.md#templates)) |
| Custom themes (`rendercv create-theme`, `--create-typst-templates`) | A `design.typ`: start from a built-in design and replace parts of it, or [write one from scratch](design.md#writing-a-design-from-scratch) |
| Arbitrary keys in entries (`revenue: $5M ARR`)                    | An entry type with that field: [Add Fields to Entries](how_to/add_fields_to_entries.md)               |
| Typst commands in text (`#emph[text]`)                            | Tag the text with `!typst`: `!typst "#emph[text]"` (Markdown still works everywhere)                  |
| `rendercv new --theme moderncv`                                   | `rendercv new --design moderncv`                                                                       |
| `rendercv render --design design.yaml`                            | `rendercv render --design design.typ`                                                                  |
| `locale.phrases.degree_with_area: DEGREE in AREA`                 | `"#degree in #area"` (the old form still works)                                                       |
| `ExperienceEntry`, `EducationEntry`, `TextEntry`, ...             | `experience`, `education`, `paragraph`, ... (you never write them in the YAML, so nothing changes)    |

## 3. Check Your Text

Your entries don't change, with two exceptions:

- **Unknown fields are errors.** RenderCV 2 ignored fields an entry type didn't have, so typos went unnoticed. RenderCV 3 reports them, with a suggestion: ``The entry type `experience` has no field `positon`. Did you mean `position`?``. Fix the typo, or [declare the field](how_to/add_fields_to_entries.md).
- **Text is printed as written.** Characters like `#`, `$`, and `@` no longer need escaping, and Typst commands in plain text are printed instead of run. Markdown (`**bold**`, `*italic*`, `[links](https://example.com)`) and `$$math$$` work as before.

Nested bullets in `highlights` work again: indent them under a bullet, or separate them with ` - `. See [Nested Bullets](yaml_input_structure/cv.md#nested-bullets).
