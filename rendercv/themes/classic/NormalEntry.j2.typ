#block(
  ((* if "\n\n" in second_column_template *))
  two-col-entry(
    left-content: ((* endif *))[
      <<first_column_first_row_template>>
    ]((* if "\n\n" in second_column_template *)),
    right-content: [
      <<second_column_template>>
    ],
  )
  ((* endif *)),
  ((* if "\n\n" not in second_column_template *))
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  ((* endif *))
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)