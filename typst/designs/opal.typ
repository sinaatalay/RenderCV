// Opal: teal accents, Lato, left-aligned text, and centered small-caps section
// titles.

#import "engine.typ": engine, resolve-options

#let opal-defaults = (
  page: (
    top_margin: 0.65in,
    bottom_margin: 0.65in,
    left_margin: 0.65in,
    right_margin: 0.65in,
    show_footer: false,
    show_top_note: false,
  ),
  typography: (
    line_spacing: 0.6em,
    alignment: "left",
    font_family: "Lato",
    font_size: (body: 10pt, name: 26pt, headline: 10pt, connections: 9pt, section_titles: 1.2em),
    small_caps: (name: false, headline: true, connections: false, section_titles: true),
    bold: (name: true, headline: false, connections: false, section_titles: false),
  ),
  colors: (
    name: rgb(0, 100, 90),
    headline: rgb(0, 80, 72),
    connections: rgb(0, 80, 72),
    section_titles: rgb(0, 100, 90),
    links: rgb(0, 100, 90),
    footer: rgb(100, 140, 135),
    top_note: rgb(100, 140, 135),
  ),
  header: (
    alignment: center,
    space_below_name: 0.3cm,
    space_below_headline: 0.3cm,
    space_below_connections: 0.6cm,
    connections: (separator: "•", show_icons: true, space_between_connections: 0.5cm),
  ),
  links: (underline: false, show_external_link_icon: false),
  section_titles: (type: "centered_without_line", line_thickness: 0.4pt, space_above: 0.55cm, space_below: 0.25cm),
  sections: (space_between_regular_entries: 1.1em, space_between_text_based_entries: 0.3em, show_time_spans_in: ()),
  entries: (
    short_second_row: true,
    side_space: 0.15cm,
    space_between_columns: 0.1cm,
    summary: (space_above: 0.04cm),
    highlights: (
      bullet: "◦",
      nested_bullet: "◦",
      space_left: 0.15cm,
      space_above: 0.04cm,
      space_between_items: 0.04cm,
      space_between_bullet_and_text: 0.5em,
    ),
  ),
)

#let opal-entries(o, parts) = {
  let (regular-entry, entry-dates, entry-body, degree-with-area, dash-location, ..) = parts
  (
    normal: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.name)#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    experience: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.company), #emph(it.position)#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      ([#strong(it.institution)#dash-location(it.location)], degree-with-area(it, ctx)),
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
  )
}

/// The Opal design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let opal(..options) = engine(
  resolve-options(opal-defaults, options.named()),
  name: "opal",
  entries: opal-entries,
)
