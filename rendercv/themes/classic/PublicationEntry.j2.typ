#block(
  ((* if "\n\n" in second_column_template *))
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