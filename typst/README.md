# RenderCV

The Typst side of [RenderCV](https://rendercv.com): the entry types, designs, and renderer behind the `rendercv` CLI and web app.

With RenderCV, a CV is a YAML file of content. What an entry is and how everything looks are written in Typst, with this package:

- **Entry types** say which fields an entry has and how it looks by default. The standard ones are `normal`, `experience`, `education`, `publication`, `one_line`, `bullet`, `numbered`, `reversed_numbered`, and `paragraph`.
- **Designs** say how the whole CV looks, and may restyle any entry type. The built-in ones are `classic`, `moderncv`, `sb2nov`, `engineeringresumes`, `engineeringclassic`, `harvard`, `ink`, `ember`, and `opal`.

RenderCV validates the YAML against the entry types, then calls `render` with the CV's data.

## A design

Put a `design.typ` next to your CV's YAML file:

```typ
#import "@preview/rendercv:3.0.0": designs

#let design = designs.classic(
  page: (size: "a4"),
  colors: (name: rgb("#004f90"), section_titles: rgb("#004f90")),
  typography: (font_family: "Source Sans 3"),
)
```

Misspelled options and values of the wrong type stop compilation with an error naming the option.

## Your own entry types

Put an `entries.typ` next to your CV's YAML file. Every entry type it exports can be used in the YAML:

```typ
#import "@preview/rendercv:3.0.0": *

#let talk = entry-type(
  doc: "A talk at a conference or event.",
  fields: (
    title: field("markdown"),
    event: field("markdown"),
    date: field("date"),
    slides: field("url", optional: true),
  ),
  // Drawn as a normal entry, so every design styles it:
  look: (it, ctx) => as-entry("normal", name: [#it.title -- #emph(it.event)], date: it.date),
)
```

Field kinds are `markdown`, `text`, `date`, `url`, `email`, `phone`, `number`, `bool`, `choice`, `list`, `bullets`, and `entries`.

## Documentation

See [docs.rendercv.com](https://docs.rendercv.com), in particular the pages on [entry types](https://docs.rendercv.com/user_guide/entry_types/) and [designs](https://docs.rendercv.com/user_guide/design/).

## License

MIT
