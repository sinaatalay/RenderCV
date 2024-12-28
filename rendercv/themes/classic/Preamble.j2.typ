
((* set page_numbering_style_placeholders = {
    "NAME": cv.name,
    "PAGE_NUMBER": "1",
    "TOTAL_PAGES": "1",
    "TODAY": today
} *))
((* set last_updated_date_style_placeholders = {
    "TODAY": today,
} *))
#import "@preview/fontawesome:0.5.0": fa-icon

#let name = "<<cv.name>>"
#let locale-catalog-page-numbering-style = "<<locale_catalog.page_numbering_style|replace_placeholders_with_actual_values(page_numbering_style_placeholders)>>"
#let locale-catalog-last-updated-date-style = "<<locale_catalog.last_updated_date_style|replace_placeholders_with_actual_values(last_updated_date_style_placeholders)>>"
#let design-page-size = "<<design.page.size>>"
#let design-section-titles-line-type = "<<design.section_titles.line_type>>"
#let design-page-show-last-updated-date = <<design.page.show_last_updated_date|lower>>
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-colors-last-updated-date-and-page-numbering = <<design.colors.last_updated_date_and_page_numbering.as_rgb()>>
#let design-links-use-external-link-icon = <<design.links.use_external_link_icon|lower>>
#let design-text-font-size = <<design.text.font_size>>
#let design-text-leading = <<design.text.leading>>
#let design-header-name-font-size = <<design.header.name_font_size>>
#let design-header-name-bold = <<design.header.name_bold|lower>>
#let design-colors-name = <<design.colors.name.as_rgb()>>
#let design-section-titles-font-size = <<design.section_titles.font_size>>
#let design-colors-section-titles = <<design.colors.section_titles.as_rgb()>>
#let design-section-titles-bold = <<design.section_titles.bold|lower>>
#let design-section-titles-line-thickness = <<design.section_titles.line_thickness>>
#let design-highlights-left-margin = <<design.highlights.left_margin>>
#let design-highlights-horizontal-space-between-bullet-and-highlights = <<design.highlights.horizontal_space_between_bullet_and_highlight>>
#let design-header-vertical-space-between-name-and-connections = <<design.header.vertical_space_between_name_and_connections>>
#let design-header-vertical-space-between-connections-and-first-section = <<design.header.vertical_space_between_connections_and_first_section>>
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-entries-vertical-space-between-entries = <<design.entries.vertical_space_between_entries>>
#let design-section-titles-vertical-space-below = <<design.section_titles.vertical_space_below>>
#let design-page-top-margin = <<design.page.top_margin>>
#let design-page-bottom-margin = <<design.page.bottom_margin>>
#let design-page-left-margin = <<design.page.left_margin>>
#let design-page-right-margin = <<design.page.right_margin>>
#let date = datetime.today()

// Metadata:
#set document(author: name, title: name + "'s CV", date: date)

// Page settings:
#set page(
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
#set text(
  font: "Charter",
  size: design-text-font-size,
  lang: "en", // TODO
  // Disable ligatures for better ATS compatibility:
  ligatures: true,
)

// Paragraph settings:
#set par(spacing: design-entries-vertical-space-between-entries, leading: design-text-leading)

// Highlights (bullets) settings:
#show list: set list(
  indent: design-highlights-left-margin,
  body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
)

// Main headi#ng settings:
#let header-font-weight
#if design-header-name-bold {
  header-font-weight = 700
} else {
  header-font-weight = 400
}
#show heading.where(level: 1): it => [
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

#let section-title-font-weight
#if design-section-titles-bold {
  section-title-font-weight = 700
} else {
  section-title-font-weight = 400
}

#show heading.where(level: 2): it => [
  #set align(left)
  #set text(size: (1em / 1.2)) // reset
  #set text(
    size: (design-section-titles-font-size),
    weight: section-title-font-weight,
    fill: design-colors-section-titles,
  )

  #if true [
    #it.body
  ] else [
    #smallcaps(it.body)
  ]
  #if design-section-titles-line-type == "partial" [
    #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
  ] else if design-section-titles-line-type == "full" [
    #v(-0.45cm)
    #line(length: 100%, stroke: design-section-titles-line-thickness)
  ]
  // Vertical space after the section title
  #v(design-section-titles-vertical-space-below)
]

// Links:
#show link: it => [
  #set text(fill: blue)
  #underline(it.body)
  #if design-links-use-external-link-icon [
    #box(
      fa-icon("external-link-alt", size: 0.6em),
      height: auto,
      baseline: -10%,
    )
  ]
]

// Last updated date text:
#if design-page-show-last-updated-date {
  place(
    top + right,
    dy: 0pt,
    text(locale-catalog-last-updated-date-style, fill: design-colors-last-updated-date-and-page-numbering),
  )
}

#let connections(connections-list) = context {
  let list-of-connections = ()
  let separator = h(0.5cm, weak: true) + " | " + h(0.5cm, weak: true)
  let starting-index = 0
  while (starting-index < connections-list.len()) {
    let left-sum-right-margin
    if type(page.margin) == "dictionary" {
      left-sum-right-margin = page.margin.left + page.margin.right
    } else {
      left-sum-right-margin = page.margin * 2
    }

    let ending-index = starting-index + 1
    while (
      measure(connections-list.slice(starting-index, ending-index).join(separator)).width
        < page.width - left-sum-right-margin
    ) {
      ending-index = ending-index + 1
      if ending-index > connections-list.len() {
        break
      }
    }
    list-of-connections.push(connections-list.slice(starting-index, ending-index - 1).join(separator))
    starting-index = ending-index
  }

  align(list-of-connections.join(linebreak()), center)
  v(1.33cm)
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
