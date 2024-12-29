((* if section_title in design.theme_specific.show_timespan_in *))
    ((* set date_and_location_strings = [entry.location, entry.date_string, entry.time_span_string]|select("!=", "") *))
((* else *))
    ((* set date_and_location_strings = [entry.location, entry.date_string]|select("!=", "") *))
((* endif *))

#block(
  ((* if entry.date_string *))
  two-col-entry(
    left-content: [
  ((* endif *))
      #set par(spacing: design-highlights-vertical-space-between-highlights)
      ((* if not (entry.doi or entry.url)*))
      <<first_column_without_url>>
      ((*- elif not entry.journal -*))
      <<first_column_without_journal>>
      ((*- else -*))
      <<first_column>>
      ((*- endif -*))
  ((* if entry.date_string *))
    ],
    right-content: [
      <<date_and_location_strings|join("\n\n")>>
    ],
  )
  ((* endif *)),
  breakable: design-entries-allow-page-break-in-entries,
)