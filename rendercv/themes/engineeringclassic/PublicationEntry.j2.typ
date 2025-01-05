#set par(spacing: design-highlights-vertical-space-between-highlights)
((* if date_and_location_column_template *))
#two-col-entry(
  left-content: [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
    <<main_column_first_row_template>>

  ((* if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" *))
    ((* if not (entry.doi or entry.url)*))
  <<main_column_second_row_without_url_template>>
    ((*- elif not entry.journal -*))
  <<main_column_second_row_without_journal_template>>
    ((*- else -*))
  <<main_column_second_row_template>>
    ((*- endif -*))
  ((* endif *))
  ],
  right-content: [
    <<date_and_location_column_template>>
  ],
)
  ((* if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv") *))
    ((* if not (entry.doi or entry.url)*))
  <<main_column_second_row_without_url_template>>
    ((*- elif not entry.journal -*))
  <<main_column_second_row_without_journal_template>>
    ((*- else -*))
  <<main_column_second_row_template>>
    ((*- endif -*))
((* endif *))
((* else *))

<<main_column_first_row_template>>

((* if not (entry.doi or entry.url)*))
<<main_column_second_row_without_url_template>>
((*- elif not entry.journal -*))
<<main_column_second_row_without_journal_template>>
((*- else -*))
<<main_column_second_row_template>>
((*- endif -*))
((* endif *))