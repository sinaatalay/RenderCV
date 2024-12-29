#block(
  ((* if entry.date_string or entry.location *))
  two-col-entry(
    left-content: [
  ((* endif *))
      <<first_column>>
  ((* if entry.date_string or entry.location *))
    ],
    right-content: [
      <<second_column>>
    ],
  )
  ((* endif *)),
  breakable: design-entries-allow-page-break-in-entries,
)