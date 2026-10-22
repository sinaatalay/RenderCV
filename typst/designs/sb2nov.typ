// Sb2nov: black and white with a full-width line under section titles, after
// Jake Gutierrez's (sb2nov) LaTeX resume.

#import "engine.typ": engine, resolve-options

#let sb2nov-defaults = (
  typography: (font_family: "New Computer Modern"),
  colors: (
    name: rgb(0, 0, 0),
    connections: rgb(0, 0, 0),
    section_titles: rgb(0, 0, 0),
    headline: rgb(0, 0, 0),
    links: rgb(0, 0, 0),
  ),
  links: (underline: true, show_external_link_icon: false),
  section_titles: (type: "with_full_line"),
  sections: (show_time_spans_in: ()),
  header: (
    connections: (
      hyperlink: true,
      show_icons: false,
      display_urls_instead_of_usernames: true,
      separator: "•",
    ),
  ),
  entries: (short_second_row: false, highlights: (bullet: "◦", nested_bullet: "◦")),
)

#let sb2nov-entries(o, parts) = {
  let (regular-entry, entry-dates, entry-body, degree-with-area, ..) = parts
  let aside(it, ctx) = (if it.location != none { emph(it.location) }, ..entry-dates(it, ctx).filter(date => date != none).map(emph))
  (
    normal: (it, ctx) => regular-entry(ctx, strong(it.name), aside(it, ctx), body: entry-body(it, ctx)),
    experience: (it, ctx) => regular-entry(
      ctx,
      (strong(it.position), emph(it.company)),
      aside(it, ctx),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      (strong(it.institution), emph(degree-with-area(it, ctx))),
      aside(it, ctx),
      body: entry-body(it, ctx),
    ),
  )
}

/// The Sb2nov design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let sb2nov(..options) = engine(
  resolve-options(sb2nov-defaults, options.named()),
  name: "sb2nov",
  entries: sb2nov-entries,
)
