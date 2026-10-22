// Classic: blue accents, section titles with a partial line, and the degree
// in its own column.

#import "engine.typ": engine, resolve-options

/// The classic design.
///
/// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
/// -> dictionary
#let classic(..options) = engine(resolve-options((:), options.named()), name: "classic")
