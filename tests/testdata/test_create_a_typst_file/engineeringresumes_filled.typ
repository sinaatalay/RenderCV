
#import "@preview/fontawesome:0.5.0": fa-icon

#let name = "John Doe"
#let locale-catalog-page-numbering-style = context { "John Doe - Page " + str(here().page()) + " of " + str(counter(page).final().first()) + "" }
#let locale-catalog-last-updated-date-style = "Last updated in Jan 2024"
#let locale-catalog-language = "en"
#let design-page-size = "us-letter"
#let design-section-titles-font-size = 1.2em
#let design-colors-text = rgb(0, 0, 0)
#let design-colors-section-titles = rgb(0, 0, 0)
#let design-colors-last-updated-date-and-page-numbering = rgb(128, 128, 128)
#let design-colors-name = rgb(0, 0, 0)
#let design-colors-connections = rgb(0, 0, 0)
#let design-colors-links = rgb(0, 0, 0)
#let design-section-titles-bold = true
#let design-section-titles-line-thickness = 0.5pt
#let design-section-titles-font-size = 1.2em
#let design-section-titles-line-type = "full"
#let design-section-titles-vertical-space-above = 0.3cm
#let design-section-titles-vertical-space-below = 0.1cm
#let design-links-use-external-link-icon = false
#let design-text-font-size = 10pt
#let design-text-leading = 0.2em
#let design-text-font-family = "Charter"
#let design-text-alignment = "justified"
#let design-header-photo-width = 3.5cm
#let design-header-use-icons-for-connections = false
#let design-header-name-font-size = 25pt
#let design-header-name-bold = false
#let design-header-vertical-space-between-name-and-connections = 0.7cm
#let design-header-vertical-space-between-connections-and-first-section = 0.7cm
#let design-header-use-icons-for-connections = false
#let design-header-horizontal-space-between-connections = 0.5cm
#let design-header-separator-between-connections = "|"
#let design-header-alignment = center
#let design-highlights-summary-left-margin = 0cm
#let design-highlights-bullet = "•"
#let design-highlights-top-margin = 0.1cm
#let design-highlights-left-margin = 0cm
#let design-highlights-vertical-space-between-highlights = 0.13cm
#let design-highlights-horizontal-space-between-bullet-and-highlights = 0.3em
#let design-entries-vertical-space-between-entries = 0.30cm
#let design-entries-date-and-location-width = 4.15cm
#let design-entries-allow-page-break-in-entries = true
#let design-entries-horizontal-space-between-columns = 0.1cm
#let design-entries-left-and-right-margin = 0cm
#let design-page-top-margin = 2cm
#let design-page-bottom-margin = 2cm
#let design-page-left-margin = 2cm
#let design-page-right-margin = 2cm
#let design-page-show-last-updated-date = true
#let design-page-show-page-numbering = false
#let design-links-underline = true
#let design-theme-specific-education-degree-width = 1cm
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
  footer: if design-page-show-page-numbering {
    text(
      fill: design-colors-last-updated-date-and-page-numbering,
      align(center, [_#locale-catalog-page-numbering-style _]),
      size: 0.9em,
    )
  } else {
    none
  },
  footer-descent: 0% - 0.3em + design-page-bottom-margin / 2,
)
// Text settings:
#let justify
#let hyphenate
#if design-text-alignment == "justified" {
  justify = true
  hyphenate = true
} else if design-text-alignment == "left" {
  justify = false
  hyphenate = false
} else if design-text-alignment == "justified-with-no-hyphenation" {
  justify = true
  hyphenate = false
}
#set text(
  font: design-text-font-family,
  size: design-text-font-size,
  lang: locale-catalog-language,
  hyphenate: hyphenate,
  fill: design-colors-text,
  // Disable ligatures for better ATS compatibility:
  ligatures: true,
)
#set par(
  spacing: 0pt,
  leading: design-text-leading,
  justify: justify,
)

// Highlights settings:
#let highlights(..content) = {
  list(
    ..content,
    marker: design-highlights-bullet,
    spacing: design-highlights-vertical-space-between-highlights,
    indent: design-highlights-left-margin,
    body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
  )
}
#show list: set list(
  marker: design-highlights-bullet,
  spacing: design-entries-vertical-space-between-entries,
  indent: 0pt,
  body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
)

// Main heading settings:
#let header-font-weight
#if design-header-name-bold {
  header-font-weight = 700
} else {
  header-font-weight = 400
}
#show heading.where(level: 1): it => [
  #set align(design-header-alignment)
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

  // Vertical space above the section title
  #v(design-section-titles-vertical-space-above, weak: true)
  #block(
    breakable: false,
    width: 100%,
    [
      #box([
        #if true [
          #it.body
        ] else [
          #smallcaps(it.body)
        ]
        #if design-section-titles-line-type == "partial" [
          #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
        ] else if design-section-titles-line-type == "full" [

          #v(design-text-font-size * 0.4)
          #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
        ]
      ])
    ] + v(1em),
  )
  #v(-1em)
  // Vertical space after the section title
  #v(design-section-titles-vertical-space-below - 0.5em)
]

// Links:
#let original-link = link
#let link(url, body) = {
  body = [#if design-links-underline [#underline(body)] else [#body]]
  body = [#if design-links-use-external-link-icon [#body#h(design-text-font-size/4)#box(
        fa-icon("external-link", size: 0.7em),
        baseline: -10%,
      )] else [#body]]
  body = [#set text(fill: design-colors-links);#body]
  original-link(url, body)
}

// Last updated date text:
#if design-page-show-last-updated-date {
  place(
    top + right,
    dy: -design-page-top-margin / 2,
    dx: -design-entries-left-and-right-margin,
    text(
      [_#locale-catalog-last-updated-date-style _],
      fill: design-colors-last-updated-date-and-page-numbering,
      size: 0.9em,
    ),
  )
}

#let connections(connections-list) = context {
  let list-of-connections = ()
  let separator = (
    h(design-header-horizontal-space-between-connections / 2, weak: true)
      + design-header-separator-between-connections
      + h(design-header-horizontal-space-between-connections / 2, weak: true)
  )
  let starting-index = 0
  while (starting-index < connections-list.len()) {
    let left-sum-right-margin
    if type(page.margin) == "dictionary" {
      left-sum-right-margin = page.margin.left + page.margin.right
    } else {
      left-sum-right-margin = page.margin * 4
    }

    let ending-index = starting-index + 1
    while (
      measure(connections-list.slice(starting-index, ending-index).join(separator)).width
        < page.width - left-sum-right-margin - design-header-photo-width * 1.1
    ) {
      ending-index = ending-index + 1
      if ending-index > connections-list.len() {
        break
      }
    }
    if ending-index > connections-list.len() {
      ending-index = connections-list.len()
    }
    list-of-connections.push(connections-list.slice(starting-index, ending-index).join(separator))
    starting-index = ending-index
  }
  set text(fill: design-colors-connections)
  set par(leading: design-text-leading*1.7, justify: false)
  align(list-of-connections.join(linebreak()), design-header-alignment)
  v(design-header-vertical-space-between-connections-and-first-section - design-section-titles-vertical-space-above)
}

#let three-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  middle-content: "",
  right-content: "",
  alignments: (left, left, right),
) = [
  #block(
    grid(
      columns: (left-column-width, 1fr, right-column-width),
      column-gutter: design-entries-horizontal-space-between-columns,
      align: alignments,
      ([#set par(spacing: design-text-leading); #left-content]),
      ([#set par(spacing: design-text-leading); #middle-content]),
      ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

#let two-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  right-content: "",
  alignments: (left, right),
  column-gutter: design-entries-horizontal-space-between-columns,
) = [
  #block(
    grid(
      columns: (left-column-width, right-column-width),
      column-gutter: column-gutter,
      align: alignments,
      ([#set par(spacing: design-text-leading); #left-content]),
      ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

#two-col-entry(
  left-column-width: design-header-photo-width * 1.1,
  right-column-width: 1fr,
  left-content: [
    #align(
      left + horizon,
      image("profile_picture.jpg", width: design-header-photo-width),
    )
  ],
  column-gutter: 0cm,
  right-content: [
= John Doe

// Print connections:
#let connections-list = (
  [Istanbul, Turkey],
  [#box(original-link("mailto:john_doe@example.com")[john\_doe\@example.com])],
  [#box(original-link("tel:+90-541-999-99-99")[0541 999 99 99])],
  [#box(original-link("https://example.com/")[example.com])],
  [#box(original-link("https://linkedin.com/in/johndoe")[linkedin.com/in/johndoe])],
  [#box(original-link("https://github.com/johndoe")[github.com/johndoe])],
  [#box(original-link("https://instagram.com/johndoe")[instagram.com/johndoe])],
  [#box(original-link("https://orcid.org/0000-0000-0000-0000")[orcid.org/0000-0000-0000-0000])],
  [#box(original-link("https://scholar.google.com/citations?user=F8IyYrQAAAAJ")[scholar.google.com/citations?user=F8IyYrQAAAAJ])],
  [#box(original-link("https://example.com/@johndoe")[example.com/\@johndoe])],
  [#box(original-link("https://stackoverflow.com/users/12323/johndoe")[stackoverflow.com/users/12323/johndoe])],
  [#box(original-link("https://gitlab.com/johndoe")[gitlab.com/johndoe])],
  [#box(original-link("https://researchgate.net/profile/johndoe")[researchgate.net/profile/johndoe])],
  [#box(original-link("https://youtube.com/@johndoe")[youtube.com/\@johndoe])],
  [#box(original-link("https://t.me/johndoe")[t.me/johndoe])],
)
#connections(connections-list)

  ],
)


== Text Entries

#block(
  [
    This is a #[_TextEntry_]. It is only a text and can be useful for sections like #[*Summary*]. To showcase the TextEntry completely, this sentence is added, but it doesn't contain any information.
  ],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    This is a #[_TextEntry_]. It is only a text and can be useful for sections like #[*Summary*]. To showcase the TextEntry completely, this sentence is added, but it doesn't contain any information.
  ],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    This is a #[_TextEntry_]. It is only a text and can be useful for sections like #[*Summary*]. To showcase the TextEntry completely, this sentence is added, but it doesn't contain any information.
  ],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)


== Bullet Entries

#block(
  [- This is a bullet entry.],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [- This is a bullet entry.],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)


== Publication Entries

#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

    J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://example.com")[example.com]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

    J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

IEEE Transactions on Applied Superconductivity  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
      J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

    J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://example.com")[example.com]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://example.com")[example.com]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
      J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

IEEE Transactions on Applied Superconductivity  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

    J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

IEEE Transactions on Applied Superconductivity

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
      J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://example.com")[example.com]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
      J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

IEEE Transactions on Applied Superconductivity

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)

    #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
J. Doe, #[*_H. Tom_*], S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname, S. Doe, A. Andsurname

#link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007/978-3-319-69626-3_101-1]

#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        #[*Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils*]

      ],
      right-content: [
        Sept 2021
      ],
    )
#two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)


== Experience Entries

#block(
  [

    #[*Software Engineer*], Some #[*Company*] --

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] --

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*Software Engineer*], Some #[*Company*] -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)


== Education Entries

#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering --

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering --

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering --

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering --

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering --

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // NO DATE, NO DEGREE

    #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering --
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*],  in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        #[*Boğaziçi University*], BS in Mechanical Engineering -- Istanbul, Turkey
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)


== Normal Entries

#block(
  [

    #[*My Project*]

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [

    #[*My Project*]

    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – present
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2015 – June 2020
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
#v(design-entries-vertical-space-between-entries)
#block(
  [
    #two-col-entry(
      left-content: [
        #[*My Project*]
      ],
      right-content: [
        Sept 2021
      ],
    )
    #two-col-entry(

  left-column-width: design-highlights-summary-left-margin,

  right-column-width: 1fr,

  left-content: [],

  right-content: [

    #v(design-highlights-top-margin)

    #align(left, [A string])

  ],

  column-gutter: 0cm,

)

  #v(design-highlights-top-margin)

  #highlights(

    [Did #[_this_] and this is a #[*bold*] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.],

    [Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.],

  )
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)


== One Line Entries

#block(
  [
    #[*Pro#[*gram*]ming:*] Python, C++, JavaScript, MATLAB
  ],
  breakable: design-entries-allow-page-break-in-entries,
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  width: 100%,
)


== A Section & with \% Special Characters

#block(
  [

    #[*A Section & with \% Special Characters*]

    
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)


