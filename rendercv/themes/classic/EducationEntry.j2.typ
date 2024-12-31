#block(
  ((* if design.entry_types.education_entry.degree_column_template *))
  three-col-entry(
    left-column-width: 1cm,
    left-content: [<<degree_column_template>>],
    middle-content: [
      <<first_column_template>>
    ],
  ((* else *))
  two-col-entry(
    left-content: [
      <<first_column_template>>
    ],
  ((* endif *))
    right-content: [
      <<second_column_template>>
    ],
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
