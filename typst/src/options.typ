// Design options: a design's defaults, merged with what the user sets.
//
// A design declares its options as a (nested) dictionary of defaults. Users
// override any of them with named arguments, e.g.
// `designs.classic(colors: (name: blue), page: (size: "a4"))`. Nested
// dictionaries merge key by key, so only the changed values need to be given.

/// Types that may stand in for each other when checking an option's value.
#let compatible-types = (
  (length, relative, ratio, fraction),
  (int, float),
  (color, gradient, tiling),
  (str, content, symbol),
)

/// Whether `value` may replace an option whose default is `default`.
#let is-compatible(value, default) = {
  if default == none or default == auto or value == none or value == auto {
    return true
  }
  if type(value) == type(default) {
    return true
  }
  compatible-types.any(group => type(value) in group and type(default) in group)
}

/// The number of single-character edits that turn one string into another.
#let edit-distance(a, b) = {
  let a = a.clusters()
  let b = b.clusters()
  let previous = range(b.len() + 1)
  for i in range(a.len()) {
    let current = (i + 1,)
    for j in range(b.len()) {
      let substitution = previous.at(j) + if a.at(i) == b.at(j) { 0 } else { 1 }
      current.push(calc.min(previous.at(j + 1) + 1, current.at(j) + 1, substitution))
    }
    previous = current
  }
  previous.last()
}

/// The option name closest to a misspelled one, if any is close enough.
#let closest-option(key, options) = {
  let (distance, closest) = options
    .map(option => (edit-distance(key, option), option))
    .sorted(key: pair => pair.first())
    .at(0, default: (none, none))
  if closest != none and distance <= calc.max(1, calc.floor(key.len() / 3)) { closest }
}

/// Merges user-set option values into a design's defaults.
///
/// Unknown options and values of the wrong type stop compilation with an error
/// naming the option.
///
/// - defaults (dictionary): The design's options and their default values.
/// - values (dictionary): The options the user set.
/// - path (str): Where in the options this dictionary is, for error messages.
/// -> dictionary
#let merge-options(defaults, values, path: "") = {
  let merged = defaults
  for (key, value) in values {
    let location = if path == "" { key } else { path + "." + key }
    if key not in defaults {
      let closest = closest-option(key, defaults.keys())
      panic(
        "Unknown design option `"
          + location
          + "`."
          + if closest != none { " Did you mean `" + closest + "`?" } else { "" }
          + " Available options here: "
          + defaults.keys().map(k => "`" + k + "`").join(", ")
          + ".",
      )
    }
    let default = defaults.at(key)
    if type(default) == dictionary and type(value) == dictionary {
      merged.insert(key, merge-options(default, value, path: location))
    } else if is-compatible(value, default) {
      merged.insert(key, value)
    } else {
      panic(
        "Design option `"
          + location
          + "` should be of type "
          + str(type(default))
          + ", but got "
          + repr(value)
          + ".",
      )
    }
  }
  merged
}
