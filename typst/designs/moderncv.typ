// ModernCV: dates on the left, section titles with a colored bar, like the
// LaTeX package of the same name.

#import "engine.typ": engine, resolve-options

#let moderncv-defaults = (
  typography: (
    line_spacing: 0.6em,
    font_family: "Fontin",
    font_size: (name: 25pt, section_titles: 1.4em),
    bold: (name: false, section_titles: false),
  ),
  header: (alignment: left, photo_width: 4.15cm, photo_space_left: 0cm, photo_space_right: 0.3cm),
  links: (underline: true, show_external_link_icon: false),
  section_titles: (type: "moderncv", space_above: 0.55cm, space_below: 0.3cm, line_thickness: 0.15cm),
  sections: (show_time_spans_in: ()),
  entries: (
    short_second_row: false,
    side_space: 0cm,
    space_between_columns: 0.3cm,
    summary: (space_above: 0.1cm),
    highlights: (space_left: 0cm, space_above: 0.15cm, space_between_items: 0.1cm, space_between_bullet_and_text: 0.3em),
  ),
)

#let moderncv-entries(o, parts) = {
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

/// The ModernCV design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let moderncv(..options) = engine(
  resolve-options(moderncv-defaults, options.named()),
  name: "moderncv",
  entries: moderncv-entries,
)
