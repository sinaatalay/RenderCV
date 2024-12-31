#block(
  ((* if entry.date_string *))
  two-col-entry(
    left-content: ((* endif *))[
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        ((* if not (entry.doi or entry.url)*))
        <<first_column_template_without_url>>
        ((*- elif not entry.journal -*))
        <<first_column_template_without_journal>>
        ((*- else -*))
        <<first_column_template>>
        ((*- endif -*))
    ]((* if entry.date_string *)),
    right-content: [
      <<second_column_template>>
    ],
  )
  ((* endif *)),
  ((* if not entry.date_string *))
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  ((* endif *))
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)