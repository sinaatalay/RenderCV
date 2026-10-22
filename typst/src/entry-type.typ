// Entry types: the vocabulary a CV is written in.
//
// An entry type declares the fields an entry may have (so RenderCV can validate
// the YAML against them) and a look: a function that turns one entry into Typst
// content. A look may also hand the entry over to another type with `as-entry`,
// so a design only has to style that other type for it to look right.

/// Declares one field of an entry type.
///
/// - kind (str): One of "markdown", "text", "date", "url", "email", "phone",
///   "number", "bool", "choice", "list", "bullets", or "entries".
/// - optional (bool): Whether the field may be left out.
/// - doc (str, none): What the field is for. Shown in editors and docs.
/// - of (str, none): The kind of each item, for "list" fields.
/// - choices (array, none): The allowed values, for "choice" fields.
/// - pattern (str, none): A regular expression "text" values must match.
/// - allow-text (bool): Whether a "date" field also accepts free text such as
///   "Fall 2023".
/// -> dictionary
#let field(
  kind,
  optional: false,
  doc: none,
  of: none,
  choices: none,
  pattern: none,
  allow-text: false,
) = (
  rendercv-field: true,
  kind: kind,
  optional: optional,
  doc: doc,
  of: of,
  choices: choices,
  pattern: pattern,
  allow-text: allow-text,
)

/// Declares an entry type.
///
/// - fields (dictionary): Field names mapped to `field(...)` declarations.
/// - look (function): `(it, ctx) => content` that draws one entry. `it` holds
///   the entry's fields; missing optional fields are `none`. It may return
///   `as-entry(...)` to be drawn as another entry type instead.
/// - doc (str, none): What the entry type is for.
/// -> dictionary
#let entry-type(fields: (:), look: none, doc: none) = (
  rendercv-entry-type: true,
  fields: fields,
  look: look,
  doc: doc,
)

/// Asks for an entry to be drawn as another entry type.
///
/// Returned from a look, this hands the entry over to `target` with the given
/// fields. The active design's look for `target` is used if it has one.
///
/// - target (str): The name of the entry type to draw the entry as.
/// - fields (arguments): The fields of the target entry type.
/// -> dictionary
#let as-entry(target, ..fields) = (
  rendercv-as: target,
  fields: fields.named(),
)

/// Whether a value is an entry type declared with `entry-type`.
#let is-entry-type(value) = (
  type(value) == dictionary and value.at("rendercv-entry-type", default: false) == true
)

/// Whether a value is a hand-over created with `as-entry`.
#let is-hand-over(value) = (
  type(value) == dictionary and value.at("rendercv-as", default: none) != none
)

/// Picks the entry types out of a module's definitions.
///
/// - definitions (dictionary): Usually `dictionary(module)`.
/// -> dictionary
#let collect-entry-types(definitions) = (
  definitions.pairs().filter(((name, value)) => is-entry-type(value)).to-dict()
)

/// Serializable field declarations of entry types, for RenderCV to validate
/// YAML against.
///
/// - types (dictionary): Entry type names mapped to entry types.
/// -> dictionary
#let declarations(types) = (
  types
    .pairs()
    .map(((name, entry-type)) => (
      name,
      (
        doc: entry-type.doc,
        fields: entry-type
          .fields
          .pairs()
          .map(((field-name, f)) => (
            field-name,
            (
              kind: f.kind,
              optional: f.optional,
              doc: f.doc,
              of: f.of,
              choices: f.choices,
              pattern: f.pattern,
              allow-text: f.allow-text,
            ),
          ))
          .to-dict(),
      ),
    ))
    .to-dict()
)
