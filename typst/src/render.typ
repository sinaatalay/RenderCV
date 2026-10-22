// Rendering: turning RenderCV's data into a document with a design.
//
// A document is a header, then sections; a section holds entries or
// subsections, and a subsection holds entries. Each entry is drawn by the
// design's look for its type if the design has one, otherwise by the entry
// type's own look. A look may hand the entry over to another entry type with
// `as-entry`, which is then drawn the same way.

#import "entry-type.typ": is-hand-over
#import "values.typ": entry-values
#import "rich.typ": rich
#import "dates.typ": normalize-date

/// The most hand-overs allowed while drawing one entry, to catch loops.
#let maximum-hand-overs = 16

/// What every design starts from: plain, semantic Typst. A design only needs to
/// replace the parts it wants to look different.
#let base-design = (
  name: "base",
  options: (:),
  /// Sets up the document and wraps its body.
  document: (body, info) => {
    set document(title: info.title, author: info.author, keywords: info.keywords)
    set text(lang: info.locale.iso_code, dir: if info.locale.direction == "rtl" { rtl } else { ltr })
    body
  },
  /// Arranges the header and the sections on the page.
  layout: (header, sections, ctx) => {
    header
    sections.map(section => section.body).join()
  },
  /// Draws the header: name, headline, photo, and connections.
  header: (header, ctx) => {
    if header.name != none {
      heading(level: 1, header.name)
    }
    if header.headline != none {
      par(header.headline)
    }
    if header.connections.len() > 0 {
      par(
        header
          .connections
          .map(connection => {
            if connection.url == none { connection.text } else { link(connection.url, connection.text) }
          })
          .join([ | ]),
      )
    }
  },
  /// Draws a section or subsection: its title, then its body.
  section: (section, body, ctx) => {
    heading(level: section.level + 1, section.title)
    body
  },
  /// Looks that replace entry types' own looks, by entry type name.
  entries: (:),
)

/// Draws one entry.
///
/// - entry (dictionary): The entry from RenderCV's data: `(type, fields)`.
/// - types (dictionary): Entry type names mapped to entry types.
/// - design (dictionary): The design.
/// - ctx (dictionary): Where the entry is and what it may need to know.
/// -> content
#let render-entry(entry, types, design, ctx) = {
  let type-name = entry.type
  let it = entry-values(entry.fields, types.at(type-name).fields)
  for hand-over in range(maximum-hand-overs) {
    let entry-ctx = ctx + (type: type-name)
    let look = design.entries.at(type-name, default: types.at(type-name).look)
    let result = look(it, entry-ctx)
    if not is-hand-over(result) {
      return result
    }
    type-name = result.rendercv-as
    if type-name not in types {
      panic("An entry was handed over to the unknown entry type `" + type-name + "`.")
    }
    let fields = types.at(type-name).fields
    it = fields.keys().map(name => (name, none)).to-dict() + result.fields
  }
  panic("An entry of type `" + entry.type + "` is handed over in a loop.")
}

/// Draws RenderCV's data as a document.
///
/// - data (dictionary): RenderCV's data: header, sections, locale, settings.
/// - types (dictionary): Entry type names mapped to entry types.
/// - design (dictionary): The design.
/// -> content
#let render(data, types: (:), design: (:)) = {
  let design = base-design + design
  let locale = data.locale
  let current-date = normalize-date(data.settings.current_date)
  let base-ctx = (
    locale: locale,
    current-date: current-date,
    settings: data.settings,
  )

  let render-entries(entries, ctx) = {
    let count = entries.len()
    entries
      .enumerate()
      .map(((index, entry)) => {
        let entry-ctx = (
          ctx
            + (
              index: index + 1,
              count: count,
              render-entries: nested => render-entries(nested, ctx),
            )
        )
        render-entry(entry, types, design, entry-ctx)
      })
      .join()
  }

  let render-section(section, level, parent) = {
    let section-info = (
      key: section.key,
      title: rich(section.title),
      level: level,
      parent: parent,
    )
    let ctx = base-ctx + (section: section-info)
    let body = (
      render-entries(section.at("entries", default: ()), ctx),
      ..section
        .at("subsections", default: ())
        .map(subsection => render-section(subsection, level + 1, section-info)),
    ).join()
    (design.section)(section-info, body, ctx)
  }

  let header = data.header
  let header = (
    name: rich(header.name),
    plain-name: header.plain_name,
    headline: rich(header.headline),
    photo: header.photo,
    connections: header.connections.map(connection => connection + (text: rich(connection.text))),
  )

  let sections = data.sections.map(section => (
    key: section.key,
    title: rich(section.title),
    body: render-section(section, 1, none),
  ))

  let info = (
    title: data.settings.pdf_title,
    author: if header.plain-name == none { () } else { (header.plain-name,) },
    keywords: data.settings.at("keywords", default: ()),
    name: header.plain-name,
    locale: locale,
    current-date: current-date,
    settings: data.settings,
  )

  let body = {
    // An empty keyword would be an empty regex, which Typst rejects:
    let keywords = data.settings.at("bold_keywords", default: ()).filter(keyword => keyword != "")
    if keywords.len() > 0 {
      // Whole words only: a boundary is required only on sides where the
      // keyword starts or ends with a word character.
      let patterns = keywords
        .sorted(key: keyword => -keyword.len())
        .map(keyword => {
          let escaped = keyword.replace(regex("[\\\\.+*?()|\\[\\]{}^$#&~-]"), m => "\\" + m.text)
          let start = if keyword.match(regex("^\\w")) != none { "\\b" } else { "" }
          let end = if keyword.match(regex("\\w$")) != none { "\\b" } else { "" }
          start + escaped + end
        })
      show regex(patterns.join("|")): it => text(weight: "bold", it)
      (design.layout)((design.header)(header, base-ctx), sections, base-ctx)
    } else {
      (design.layout)((design.header)(header, base-ctx), sections, base-ctx)
    }
  }

  (design.document)(body, info)
}
