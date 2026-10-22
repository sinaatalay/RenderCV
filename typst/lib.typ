// RenderCV: a Typst framework for CVs and resumes.
//
// - Entry types (`entry-type`, `field`) say what an entry holds and how it
//   looks by default. The standard ones are `normal`, `experience`,
//   `education`, `publication`, `one_line`, `bullet`, `numbered`,
//   `reversed_numbered`, and `paragraph`.
// - Designs (`designs.classic()`, …) say how a whole CV looks, and may restyle
//   any entry type.
// - `render` draws a CV from RenderCV's data with a set of entry types and a
//   design.

#import "src/entry-type.typ": entry-type, field, as-entry, collect-entry-types, declarations
#import "src/rich.typ": rich
#import "src/dates.typ": format-date, format-dates, format-time-span
#import "src/values.typ": bullet-list
#import "src/options.typ": merge-options
#import "src/render.typ": render, base-design
#import "src/markdown.typ": to-markdown, to-markdown-document
#import "entries/standard.typ": (
  normal,
  experience,
  education,
  publication,
  one_line,
  bullet,
  numbered,
  reversed_numbered,
  paragraph,
)
#import "designs/designs.typ"
