// Engineering Classic: the classic design's colors with the Engineering
// Resumes arrangement and Raleway.

#import "engine.typ": engine, resolve-options
#import "engineeringresumes.typ": engineering-entries

#let engineeringclassic-defaults = (
  typography: (font_family: "Raleway", bold: (name: false, section_titles: false)),
  header: (alignment: left),
  links: (show_external_link_icon: false),
  section_titles: (type: "with_full_line"),
  sections: (show_time_spans_in: ()),
  entries: (
    short_second_row: false,
    summary: (space_above: 0.12cm),
    highlights: (space_left: 0cm, space_above: 0.12cm, space_between_items: 0.12cm),
  ),
)

/// The Engineering Classic design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let engineeringclassic(..options) = engine(
  resolve-options(engineeringclassic-defaults, options.named()),
  name: "engineeringclassic",
  entries: engineering-entries,
)
