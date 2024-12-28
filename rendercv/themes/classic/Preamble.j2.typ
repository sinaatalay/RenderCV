#import "@preview/fontawesome:0.5.0": fa-icon

((* set page_numbering_style_placeholders = {
    "NAME": cv.name,
    "PAGE_NUMBER": "1",
    "TOTAL_PAGES": "1",
    "TODAY": today
} *))
((* set last_updated_date_style_placeholders = {
    "TODAY": today,
} *))

#let rendercv(
  name: "<<cv.name>>",
  paper: "<<design.page.size>>",
  page-numbering-style: "<<locale_catalog.page_numbering_style|replace_placeholders_with_actual_values(page_numbering_style_placeholders)>>",
  section-title-line-type: "<<design.section_titles.line_type>>",
  show-last-updated-date: <<design.page.show_last_updated_date|lower>>,
  use-icons-for-connections: <<design.header.use_icons_for_connections|lower>>,
  last-updated-date-style: "<<locale_catalog.last_updated_date_style|replace_placeholders_with_actual_values(last_updated_date_style_placeholders)>>",
  last-updated-date-and-page-numbering-color: <<design.colors.last_updated_date_and_page_numbering.as_rgb()>>,
  use-external-link-icon: <<design.links.use_external_link_icon|lower>>,
  font-size: <<design.text.font_size>>,
  leading: <<design.text.leading>>,
  header-font-size: <<design.header.name_font_size>>,
  header-font-bold: <<design.header.name_bold|lower>>,
  header-color: <<design.colors.name.as_rgb()>>,
  section-title-font-size: <<design.section_titles.font_size>>,
  section-titles-color: <<design.colors.section_titles.as_rgb()>>,
  section-title-bold: <<design.section_titles.bold|lower>>,
  section-title-line-thickness: <<design.section_titles.line_thickness>>,
  margin-highlights-area-left-space: <<design.highlights.left_margin>>,
  margin-highlights-area-space-between-bullet-and-highlight: <<design.highlights.horizontal_space_between_bullet_and_highlight>>,
  margin-vertical-space-between-name-and-connections: <<design.header.vertical_space_between_name_and_connections>>,
  margin-vertical-space-between-connections-and-body: <<design.header.vertical_space_between_connections_and_first_section>>,
  margin-vertical-space-between-entries: <<design.entries.vertical_space_between_entries>>,
  margin-section-title-bottom: <<design.section_titles.vertical_space_below>>,
  margin-page-top: <<design.page.top_margin>>,
  margin-page-bottom: <<design.page.bottom_margin>>,
  margin-page-left: <<design.page.left_margin>>,
  margin-page-right: <<design.page.right_margin>>,

  date: datetime.today(),
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
    numbering: page-numbering-style,
    footer-descent: 0% - 0.3em + margin-page-bottom / 2,
  )

  // Text settings:
  set text(
    font: "Charter",
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
  let header-font-weight
  if header-font-bold {
    header-font-weight = 700
  } else {
    header-font-weight = 400
  }
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

  let section-title-font-weight
  if section-title-bold {
    section-title-font-weight = 700
  } else {
    section-title-font-weight = 400
  }

  show heading.where(level: 2): it => [
    #set align(left)
    #set text(size: (1em / 1.2)) // reset
    #set text(size: (section-title-font-size), weight: section-title-font-weight)

    #if true [
      #it.body
    ] else [
      #smallcaps(it.body)
    ]
    #if section-title-line-type == "partial" [
      #box(width: 1fr, height: section-title-line-thickness, fill: <<design.colors.section_titles.as_rgb()>>)
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
    #if not use-external-link-icon [
      #box(
        fa-icon("external-link-alt", size: 0.6em),
        height: auto,
        baseline: -10%,
      )
    ]
  ]

  // Last updated date text:
  if show-last-updated-date {
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
  left-column-width: 1fr,
  right-column-width: 1fr,
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
