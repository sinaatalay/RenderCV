// Ink: EB Garamond, deep indigo, and small-caps section titles without lines.

#import "engine.typ": engine, resolve-options

#let ink-defaults = (
  page: (top_margin: 0.6in, bottom_margin: 0.6in, left_margin: 0.6in, right_margin: 0.6in),
  typography: (
    line_spacing: 0.55em,
    alignment: "justified",
    font_family: "EB Garamond",
    font_size: (body: 10pt, name: 32pt, headline: 11pt, connections: 10pt, section_titles: 1.4em),
    small_caps: (name: false, headline: false, section_titles: true),
    bold: (name: true, headline: false, connections: false, section_titles: true),
  ),
  colors: (
    name: rgb(42, 24, 82),
    headline: rgb(42, 24, 82),
    connections: rgb(70, 50, 110),
    section_titles: rgb(42, 24, 82),
    links: rgb(42, 24, 82),
    footer: rgb(120, 100, 140),
    top_note: rgb(120, 100, 140),
  ),
  header: (
    alignment: left,
    space_below_name: 0.5cm,
    space_below_headline: 0.4cm,
    space_below_connections: 0.5cm,
    connections: (
      separator: "|",
      show_icons: false,
      display_urls_instead_of_usernames: true,
      space_between_connections: 0.4cm,
    ),
  ),
  links: (underline: true, show_external_link_icon: false),
  section_titles: (type: "without_line", space_above: 0.5cm, space_below: 0.2cm),
  sections: (space_between_regular_entries: 1em, space_between_text_based_entries: 0.2em, show_time_spans_in: ()),
  entries: (
    short_second_row: false,
    side_space: 0cm,
    space_between_columns: 0.2cm,
    summary: (space_above: 0.06cm),
    highlights: (
      bullet: "•",
      nested_bullet: "•",
      space_left: 0cm,
      space_above: 0.06cm,
      space_between_items: 0.06cm,
      space_between_bullet_and_text: 0.4em,
    ),
  ),
)

/// Entry looks with the location after the title and the role in italics on
/// the next line. Shared by Ink and Ember.
#let two-line-entries(o, parts, bold-normal-location: true) = {
  let (regular-entry, entry-dates, entry-body, degree-with-area, dash-location, ..) = parts
  (
    normal: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.name)#dash-location(if it.location != none and bold-normal-location { strong(it.location) } else { it.location })],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    experience: (it, ctx) => regular-entry(
      ctx,
      ([#strong(it.company)#dash-location(it.location)], emph(it.position)),
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      ([#strong(it.institution)#dash-location(it.location)], emph(degree-with-area(it, ctx))),
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
  )
}

/// The Ink design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let ink(..options) = engine(
  resolve-options(ink-defaults, options.named()),
  name: "ink",
  entries: two-line-entries,
)
