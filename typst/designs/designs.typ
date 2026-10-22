// The built-in designs.
//
// Each design is a function: call it with the options to change, e.g.
// `designs.classic(colors: (name: blue), page: (size: "a4"))`. To build your
// own on the same engine, use `designs.engine(designs.resolve-options(...))`,
// or start from a built-in design and replace any part of it:
// `designs.classic() + (section: (section, body, ctx) => ...)`.

#import "engine.typ": engine, resolve-options, defaults
#import "classic.typ": classic
#import "moderncv.typ": moderncv
#import "sb2nov.typ": sb2nov
#import "engineeringresumes.typ": engineeringresumes
#import "engineeringclassic.typ": engineeringclassic
#import "harvard.typ": harvard
#import "ink.typ": ink
#import "ember.typ": ember
#import "opal.typ": opal

/// The names of the built-in designs.
#let names = (
  "classic",
  "moderncv",
  "sb2nov",
  "engineeringresumes",
  "engineeringclassic",
  "harvard",
  "ink",
  "ember",
  "opal",
)
