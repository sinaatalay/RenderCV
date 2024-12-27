#import "@preview/fontawesome:0.5.0": fa-icon

#let rendercv(
  name: none,
  accent-color: gray,
  date: datetime.today(),
  paper: "us-letter",
  page_numbering_style: "1 of 1",
  section-title-line-type: "partial",
  disable-last-updated-date: false,
  disable-connections-icon: false,
  last-updated-date-style: "Last updated in " + datetime.today().display(),
  last-updated-date-and-page-numbering-color: gray,
  disable-external-link-icon: false,
  font-size: 10pt,
  leading: 1.2em,
  section-title-font-scale: 1.2em,
  header-font-size: 30pt,
  header-font-weight: 700,
  header-color: blue,
  section-title-font-weight: 400,
  section-title-line-thickness: 0.5pt,
  margin-highlights-area-left-space: 0.5in,
  margin-highlights-area-space-between-bullet-and-highlight: 0.5em,
  margin-vertical-space-between-name-and-connections: 0.5cm,
  margin-vertical-space-between-connections-and-body: 0.5cm,
  margin-vertical-space-between-entries: 0.5cm,
  margin-section-title-bottom: 0.5cm,
  margin-page-top: 0.5in,
  margin-page-bottom: 0.5in,
  margin-page-left: 0.5in,
  margin-page-right: 0.5in,
  body,
) = {
  // Metadata:
  let pdf-author
  if name == none {
    pdf-author = "Anonymous"
  } else {
    pdf-author = name
  }
  set document(author: pdf-author, title: pdf-author + "'s CV", date: date)

  // Page settings:
  set page(
    margin: (
      top: margin-page-top,
      bottom: margin-page-bottom,
      left: margin-page-left,
      right: margin-page-right,
    ),
    paper: paper,
    numbering: page_numbering_style,
    footer-descent: 0% - 0.3em + margin-page-bottom / 2,
  )

  // Text settings:
  set text(
    font: "Noto Sans Batak",
    size: font-size,
    lang: "en", // TODO
    // Disable ligatures for better ATS compatibility:
    ligatures: true,
  )

  // Paragraph settings:
  set par(spacing: margin-vertical-space-between-entries, leading: leading)

  // Highlights (bullets) settings:
  show list: set list(
    indent: margin-highlights-area-left-space,
    body-indent: margin-highlights-area-space-between-bullet-and-highlight,
  )

  // Main heading settings:
  show heading.where(level: 1): it => [
    #set align(center)
    #set text(
      weight: header-font-weight,
      size: header-font-size,
      fill: header-color,
    )
    #it.body
    // Vertical space after the name
    #v(margin-vertical-space-between-name-and-connections)
  ]

  show heading.where(level: 2): it => [
    #set align(left)
    #set text(size: (section-title-font-scale / 1.2), weight: section-title-font-weight)

    #if true [
      #it.body
    ] else [
      #smallcaps(it.body)
    ]
    #if section-title-line-type == "partial" [
      #box(width: 1fr, height: section-title-line-thickness, fill: rgb(accent-color))
    ] else if section-title-line-type == "full" [
      #v(-0.45cm)
      #line(length: 100%, stroke: section-title-line-thickness)
    ]
    // Vertical space after the section title
    #v(margin-section-title-bottom)
  ]

  // Links:
  show link: it => [
    #set text(fill: blue)
    #underline(it.body)
    #if not disable-external-link-icon [
      #box(
        fa-icon("external-link-alt", size: 0.6em),
        height: auto,
        baseline: -10%,
      )
    ]
  ]

  // Last updated date text:
  if disable-last-updated-date {
    place(
      top + right,
      dy: 0pt,
      text(last-updated-date-style, fill: last-updated-date-and-page-numbering-color),
    )
  }

  body
}

#let connection(url, text_url, icon: "") = {
  if icon != "" {
    return link(url)[#text_url]
  } else {
    return link(url)[#icon + " " + text_url]
  }
}

#let three-col-entry(
  left-column-width: length,
  right-column-width: length,
  left-content: "",
  middle-content: "",
  right-content: "",
) = [
  #grid(
    columns: (left-column-width, 1fr, right-column-width),
    column-gutter: 0in,
    align: (left, left, right),
    left-content, middle-content, right-content,
  )
]

#let two-col-entry(
  left-column-width: 1fr,
  right-column-width: 1fr,
  left-content: "",
  right-content: "",
) = [
  #grid(
    columns: (left-column-width, right-column-width),
    column-gutter: 0in,
    left-content, right-content,
  )
]
