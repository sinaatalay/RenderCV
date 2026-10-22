// Field values: turning the data RenderCV sends into Typst values.
//
// Each field kind arrives in one JSON shape and is handed to looks as one Typst
// value, so a look never has to parse anything:
//
// | kind       | look receives                                        |
// |------------|------------------------------------------------------|
// | markdown   | content                                              |
// | text, url, email, choice | str                                    |
// | date       | a dictionary, see `dates.typ`                        |
// | phone      | (e164, international, national, uri)                 |
// | number, bool | number, bool                                       |
// | list       | an array of the item kind's values                   |
// | bullets    | an array of (body: content, children: array)         |
// | entries    | an array of entries for `ctx.render-entries`         |

#import "rich.typ": rich
#import "dates.typ": normalize-date

/// Turns one field value from RenderCV's data into the value a look receives.
///
/// - value (any): The JSON value, or `none` if the field was left out.
/// - declaration (dictionary): The field's `field(...)` declaration.
/// -> any
#let field-value(value, declaration) = {
  if value == none {
    return none
  }
  let kind = declaration.kind
  if kind == "markdown" {
    return rich(value)
  }
  if kind == "date" {
    return normalize-date(value)
  }
  if kind == "bullets" {
    let to-bullet(item) = (
      body: rich(item.body),
      children: item.at("children", default: ()).map(to-bullet),
    )
    return value.map(to-bullet)
  }
  if kind == "list" {
    let item-declaration = (kind: declaration.of, of: none)
    return value.map(item => field-value(item, item-declaration))
  }
  value
}

/// Turns all fields of an entry into the values its look receives.
///
/// Every declared field is present in the result; fields left out are `none`.
///
/// - values (dictionary): The entry's field values from RenderCV's data.
/// - fields (dictionary): The entry type's field declarations.
/// -> dictionary
#let entry-values(values, fields) = (
  fields
    .pairs()
    .map(((name, declaration)) => (name, field-value(values.at(name, default: none), declaration)))
    .to-dict()
)

/// Draws bullets as a (nested) Typst list.
///
/// - bullets (array, none): Bullets as looks receive them.
/// -> content, none
#let bullet-list(bullets) = {
  if bullets == none or bullets.len() == 0 {
    return none
  }
  list(
    ..bullets.map(bullet => {
      bullet.body
      if bullet.children.len() > 0 {
        bullet-list(bullet.children)
      }
    }),
  )
}
