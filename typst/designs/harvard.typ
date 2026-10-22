// Harvard: the plain, serif style of Harvard's career office resume template.

#import "engine.typ": engine, resolve-options

#let harvard-defaults = (
  page: (top_margin: 0.5in, bottom_margin: 0.5in, left_margin: 0.5in, right_margin: 0.5in, show_top_note: false),
  colors: (
    name: rgb(0, 0, 0),
    headline: rgb(0, 0, 0),
    connections: rgb(0, 0, 0),
    section_titles: rgb(0, 0, 0),
    links: rgb(0, 0, 0),
  ),
  typography: (font_family: "XCharter", font_size: (name: 25pt, connections: 9pt, section_titles: 1.3em)),
  header: (
    space_below_name: 0.5cm,
    space_below_headline: 0.5cm,
    space_below_connections: 0.5cm,
    connections: (show_icons: false, separator: "•", space_between_connections: 0.4cm),
  ),
  section_titles: (type: "centered_with_centered_partial_line", space_below: 0.2cm),
  sections: (space_between_regular_entries: 1em, show_time_spans_in: ()),
  entries: (short_second_row: false),
)

#let harvard-entries(o, parts) = {
  let (regular-entry, entry-dates, entry-body, degree-with-area, dash-location, ..) = parts
  (
    normal: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.name)#dash-location(if it.location != none { strong(it.location) })],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    experience: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.company), #it.position#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.institution), #degree-with-area(it, ctx)#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
      degree: if it.degree != none { strong(it.degree) },
    ),
  )
}

/// The Harvard design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let harvard(..options) = engine(
  resolve-options(harvard-defaults, options.named()),
  name: "harvard",
  entries: harvard-entries,
)
