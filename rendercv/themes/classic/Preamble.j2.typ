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
  design-page-size: "<<design.page.size>>",
  locale-catalog-page-numbering-style: "<<locale_catalog.page_numbering_style|replace_placeholders_with_actual_values(page_numbering_style_placeholders)>>",
  locale-catalog-last-updated-date-style: "<<locale_catalog.last_updated_date_style|replace_placeholders_with_actual_values(last_updated_date_style_placeholders)>>",
  design-section-titles-line-type: "<<design.section_titles.line_type>>",
  design-page-show-last-updated-date: <<design.page.show_last_updated_date|lower>>,
  design-header-use-icons-for-connections: <<design.header.use_icons_for_connections|lower>>,
  design-colors-last-updated-date-and-page-numbering: <<design.colors.last_updated_date_and_page_numbering.as_rgb()>>,
  design-links-use-external-link-icon: <<design.links.use_external_link_icon|lower>>,
  design-text-font-size: <<design.text.font_size>>,
  design-text-leading: <<design.text.design-text-leading>>,
  design-header-name-font-size: <<design.header.name_font_size>>,
  design-header-name-bold: <<design.header.name_bold|lower>>,
  design-colors-name: <<design.colors.name.as_rgb()>>,
  design-section-titles-font-size: <<design.section_titles.font_size>>,
  design-colors-section-titles: <<design.colors.section_titles.as_rgb()>>,
  design-section-titles-bold: <<design.section_titles.bold|lower>>,
  design-section-titles-line-thickness: <<design.section_titles.line_thickness>>,
  design-highlights-left-margin: <<design.highlights.left_margin>>,
  design-highlights-horizontal-space-between-bullet-and-highlights: <<design.highlights.horizontal_space_between_bullet_and_highlight>>,
  design-header-vertical-space-between-name-and-connections: <<design.header.vertical_space_between_name_and_connections>>,
  design-header-vertical-space-between-connections-and-first-section: <<design.header.vertical_space_between_connections_and_first_section>>,
  design-entries-vertical-space-between-entries: <<design.entries.vertical_space_between_entries>>,
  design-section-titles-vertical-space-below: <<design.section_titles.vertical_space_below>>,
  design-page-top-margin: <<design.page.top_margin>>,
  design-page-bottom-margin: <<design.page.bottom_margin>>,
  design-page-left-margin: <<design.page.left_margin>>,
  design-page-right-margin: <<design.page.right_margin>>,

  date: datetime.today(),
  body,
) = {
  // Metadata:
  set document(author: name, title: name + "'s CV", date: date)

  // Page settings:
  set page(
    margin: (
      top: design-page-top-margin,
      bottom: design-page-bottom-margin,
      left: design-page-left-margin,
      right: design-page-right-margin,
    ),
    paper: design-page-size,
    numbering: locale-catalog-page-numbering-style,
    footer-descent: 0% - 0.3em + design-page-bottom-margin / 2,
  )

  // Text settings:
  set text(
    font: "Charter",
    size: design-text-font-size,
    lang: "en", // TODO
    // Disable ligatures for better ATS compatibility:
    ligatures: true,
  )

  // Paragraph settings:
  set par(spacing: design-entries-vertical-space-between-entries, design-text-leading: design-text-leading)

  // Highlights (bullets) settings:
  show list: set list(
    indent: design-highlights-left-margin,
    body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
  )

  // Main heading settings:
  let header-font-weight
  if design-header-name-bold {
    header-font-weight = 700
  } else {
    header-font-weight = 400
  }
  show heading.where(level: 1): it => [
    #set align(center)
    #set text(
      weight: header-font-weight,
      size: design-header-name-font-size,
      fill: design-colors-name,
    )
    #it.body
    // Vertical space after the name
    #v(design-header-vertical-space-between-name-and-connections)
  ]

  let section-title-font-weight
  if design-section-titles-bold {
    section-title-font-weight = 700
  } else {
    section-title-font-weight = 400
  }

  show heading.where(level: 2): it => [
    #set align(left)
    #set text(size: (1em / 1.2)) // reset
    #set text(size: (design-section-titles-font-size), weight: section-title-font-weight)

    #if true [
      #it.body
    ] else [
      #smallcaps(it.body)
    ]
    #if design-section-titles-line-type == "partial" [
      #box(width: 1fr, height: design-section-titles-line-thickness, fill: <<design.colors.section_titles.as_rgb()>>)
    ] else if design-section-titles-line-type == "full" [
      #v(-0.45cm)
      #line(length: 100%, stroke: design-section-titles-line-thickness)
    ]
    // Vertical space after the section title
    #v(design-section-titles-vertical-space-below)
  ]

  // Links:
  show link: it => [
    #set text(fill: blue)
    #underline(it.body)
    #if not design-links-use-external-link-icon [
      #box(
        fa-icon("external-link-alt", size: 0.6em),
        height: auto,
        baseline: -10%,
      )
    ]
  ]

  // Last updated date text:
  if design-page-show-last-updated-date {
    place(
      top + right,
      dy: 0pt,
      text(locale-catalog-last-updated-date-style, fill: design-colors-last-updated-date-and-page-numbering),
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
