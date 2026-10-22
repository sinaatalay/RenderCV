// Engineering Resumes: a compact, black and white design following the
// r/EngineeringResumes guidelines.

#import "engine.typ": engine, resolve-options

#let engineeringresumes-defaults = (
  page: (show_footer: false),
  typography: (font_family: "XCharter", font_size: (name: 25pt, section_titles: 1.2em), bold: (name: false)),
  header: (connections: (separator: "|", show_icons: false, display_urls_instead_of_usernames: true)),
  colors: (
    name: rgb(0, 0, 0),
    connections: rgb(0, 0, 0),
    headline: rgb(0, 0, 0),
    section_titles: rgb(0, 0, 0),
    links: rgb(0, 0, 0),
  ),
  links: (underline: true, show_external_link_icon: false),
  section_titles: (type: "with_full_line", space_above: 0.5cm, space_below: 0.3cm),
  sections: (space_between_regular_entries: 0.42cm, space_between_text_based_entries: 0.15cm, show_time_spans_in: ()),
  entries: (
    short_second_row: false,
    summary: (space_above: 0.08cm),
    side_space: 0cm,
    highlights: (
      bullet: text(13pt, [•], baseline: -0.6pt),
      nested_bullet: text(13pt, [•], baseline: -0.6pt),
      space_left: 0cm,
      space_above: 0.08cm,
      space_between_items: 0.08cm,
      space_between_bullet_and_text: 0.3em,
    ),
  ),
)

#let engineering-entries(o, parts) = {
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
      [#strong(it.position), #it.company#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.institution), #degree-with-area(it, ctx)#dash-location(it.location)],
      entry-dates(it, ctx),
      body: entry-body(it, ctx),
    ),
  )
}

/// The Engineering Resumes design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let engineeringresumes(..options) = engine(
  resolve-options(engineeringresumes-defaults, options.named()),
  name: "engineeringresumes",
  entries: engineering-entries,
)
