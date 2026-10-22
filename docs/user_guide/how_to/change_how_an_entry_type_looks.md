# Change How an Entry Type Looks

Design options change colors, fonts, and spacing. To change what an entry shows or how it is arranged, give the entry type a new look in `design.typ`. A look is a Typst function `(it, ctx) => content`, where `it` holds the entry's fields (see [Looks](../entry_types.md#looks)).

## Replace One Look in a Built-in Design

A design is a Typst dictionary, and its `entries` maps entry type names to looks. Start from a built-in design and replace the looks you want:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let base = designs.sb2nov()
#let design = base + (
  entries: base.entries + (
    one_line: (it, ctx) => block(inset: (left: 0.2cm), below: 0.8em)[#smallcaps(it.label) · #it.details],
  ),
)
```

Everything else stays sb2nov. The new look draws the entry itself, so its spacing is up to you.

## Keep the Design's Columns and Spacing

The built-in designs come with the building blocks their own looks use, in `parts`: `regular-entry` for the main column and the date and location column, `entry-dates`, `entry-body` for the summary and highlights, and [more](../design.md#changing-how-entries-look). A look built from them fits the design's columns and spacing. This design is `moderncv` with experience entries showing the position first:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let base = designs.moderncv(page: (size: "a4"))
#let (regular-entry, entry-dates, entry-body, ..) = base.parts
#let design = base + (
  entries: base.entries + (
    experience: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.position) at #it.company],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
  ),
)
```

The parts use the design's options, including your changes (`base.options` holds them).

## Give Your Own Entry Type a Look

Designs can style [your own entry types](../entry_types.md#your-own-entry-types) by their names. With the `talk` entry type from `rendercv new --entries`, this draws the event on its own line:

```typst title="design.typ"
#import "@preview/rendercv:3.0.0": designs

#let base = designs.classic()
#let (regular-entry, entry-dates, ..) = base.parts
#let design = base + (
  entries: base.entries + (
    talk: (it, ctx) => regular-entry(ctx, (strong(it.title), emph(it.event)), entry-dates(it, ctx)),
  ),
)
```

Without a look in the design, an entry type uses its own look from `entries.typ`.

!!! tip
    Typst can't call a function stored in a dictionary with `base.parts.regular-entry(...)`. Destructure it first, as above, or write `(base.parts.regular-entry)(...)`.
