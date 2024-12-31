#block(
  ((* if entry.date_string or entry.location *))
  two-col-entry(
    left-content: ((* endif *))[
        <<first_column_template>>
    ]
  ((* if entry.date_string or entry.location *))
    ,
    right-content: [
      <<second_column_template>>
    ],
  )
  ((* endif *)),
  ((* if not (entry.date_string or entry.location) *))
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  ((* endif *))
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)