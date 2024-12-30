#block(
  ((* if entry.date_string or entry.location *))
  two-col-entry(
    left-content: [
  ((* endif *))
      <<first_column_template>>
  ((* if entry.date_string or entry.location *))
    ],
    right-content: [
      <<second_column_template>>
    ],
  )
  ((* endif *)),
  breakable: design-entries-allow-page-break-in-entries,
)