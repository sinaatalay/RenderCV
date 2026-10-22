// The standard entry types.
//
// These are written exactly like entry types anyone can write in their own
// `entries.typ`. Their looks are plain and semantic; designs restyle them.
// Most of them hand over to `normal`, so a design that only styles `normal`
// already draws every one of them in its own style.

#import "../src/entry-type.typ": entry-type, field, as-entry
#import "../src/values.typ": bullet-list
#import "../src/dates.typ": format-dates

// Fields many entry types share.
#let when-fields = (
  date: field(
    "date",
    optional: true,
    allow-text: true,
    doc: "When it happened: YYYY-MM-DD, YYYY-MM, YYYY, or free text like \"Fall 2023\". For a range, use `start_date` and `end_date` instead.",
  ),
  start_date: field("date", optional: true, doc: "When it started: YYYY-MM-DD, YYYY-MM, or YYYY."),
  end_date: field(
    "date",
    optional: true,
    doc: "When it ended: YYYY-MM-DD, YYYY-MM, YYYY, or \"present\". Leave it out for something ongoing.",
  ),
)
#let detail-fields = (
  location: field("markdown", optional: true, doc: "Where it happened."),
  summary: field("markdown", optional: true, doc: "A short description."),
  highlights: field(
    "bullets",
    optional: true,
    doc: "Bullet points. Put \" - \" inside a bullet to start nested bullets.",
  ),
)

/// The general entry type, and the one other types hand over to.
#let normal = entry-type(
  doc: "A general entry with a name: a project, an award, an activity.",
  fields: (name: field("markdown", doc: "The name of the entry.")) + when-fields + detail-fields,
  look: (it, ctx) => {
    heading(level: ctx.section.level + 2, it.name)
    let when = format-dates(ctx.locale, date: it.date, start: it.start_date, end: it.end_date)
    let details = (it.location, when).filter(detail => detail != none)
    if details.len() > 0 {
      par(details.join([ | ]))
    }
    if it.summary != none {
      par(it.summary)
    }
    bullet-list(it.highlights)
  },
)

/// A job, internship, or other position.
#let experience = entry-type(
  doc: "A position at a company or organization.",
  fields: (
    company: field("markdown", doc: "The company or organization."),
    position: field("markdown", doc: "The job title."),
  )
    + when-fields
    + detail-fields,
  look: (it, ctx) => as-entry(
    "normal",
    name: [#it.company, #it.position],
    date: it.date,
    start_date: it.start_date,
    end_date: it.end_date,
    location: it.location,
    summary: it.summary,
    highlights: it.highlights,
  ),
)

/// Writes "PhD in Computer Science" with the locale's phrase, or only the area
/// if there is no degree.
#let degree-with-area(it, ctx) = {
  if it.degree == none {
    return it.area
  }
  eval(ctx.locale.phrases.degree_with_area, mode: "markup", scope: (degree: it.degree, area: it.area))
}

/// A degree or other education.
#let education = entry-type(
  doc: "A degree, diploma, or other education.",
  fields: (
    institution: field("markdown", doc: "The school or university."),
    area: field("markdown", doc: "The field of study."),
    degree: field("markdown", optional: true, doc: "The degree, such as BS, MS, or PhD."),
  )
    + when-fields
    + detail-fields,
  look: (it, ctx) => as-entry(
    "normal",
    name: [#it.institution, #degree-with-area(it, ctx)],
    date: it.date,
    start_date: it.start_date,
    end_date: it.end_date,
    location: it.location,
    summary: it.summary,
    highlights: it.highlights,
  ),
)

/// Writes a publication's link: its DOI if it has one, otherwise its URL.
#let publication-link(it) = {
  if it.doi != none {
    link("https://doi.org/" + it.doi, it.doi)
  } else if it.url != none {
    link(it.url, it.url.replace(regex("^https?://(www\\.)?"), "").trim("/", at: end))
  }
}

/// A paper, article, book, or other publication.
#let publication = entry-type(
  doc: "A paper, article, book, or other publication.",
  fields: (
    title: field("markdown", doc: "The title."),
    authors: field("list", of: "markdown", doc: "The authors. Put your own name in **double asterisks** to bold it."),
    summary: field("markdown", optional: true, doc: "A short description."),
    doi: field("text", optional: true, pattern: "10\\..+", doc: "The DOI, such as 10.48550/arXiv.2310.03138."),
    url: field("url", optional: true, doc: "A link to the publication. Used only if there is no DOI."),
    journal: field("markdown", optional: true, doc: "The journal, conference, or venue."),
    date: when-fields.date,
  ),
  look: (it, ctx) => {
    let venue = (publication-link(it), if it.journal != none [(#it.journal)]).filter(part => part != none)
    as-entry(
      "normal",
      name: it.title,
      date: it.date,
      summary: (it.summary, it.authors.join(", "), if venue.len() > 0 { venue.join(" ") })
        .filter(part => part != none)
        .join(linebreak()),
    )
  },
)

/// A label and its details on one line, like "Languages: English, Turkish".
#let one_line = entry-type(
  doc: "A label and its details on one line, like \"Languages: English, Turkish\".",
  fields: (
    label: field("markdown", doc: "The label, such as Languages."),
    details: field("markdown", doc: "The details."),
  ),
  look: (it, ctx) => par[#strong[#it.label:] #it.details],
)

/// One bullet point.
#let bullet = entry-type(
  doc: "One bullet point.",
  fields: (bullet: field("markdown", doc: "The text of the bullet point.")),
  look: (it, ctx) => list(it.bullet),
)

/// One item of a numbered list: 1, 2, 3, …
#let numbered = entry-type(
  doc: "One item of a numbered list: 1, 2, 3, …",
  fields: (number: field("markdown", doc: "The text of the item.")),
  look: (it, ctx) => enum(enum.item(ctx.index, it.number)),
)

/// One item of a list numbered backwards, so the latest item has the highest
/// number: …, 3, 2, 1.
#let reversed_numbered = entry-type(
  doc: "One item of a list numbered backwards, so the latest item has the highest number.",
  fields: (reversed_number: field("markdown", doc: "The text of the item.")),
  look: (it, ctx) => enum(enum.item(ctx.count - ctx.index + 1, it.reversed_number)),
)

/// A paragraph of text. In the YAML, a section entry that is only text is a
/// paragraph.
#let paragraph = entry-type(
  doc: "A paragraph of text. An entry written as plain text is a paragraph.",
  fields: (text: field("markdown", doc: "The text.")),
  look: (it, ctx) => par(it.text),
)
