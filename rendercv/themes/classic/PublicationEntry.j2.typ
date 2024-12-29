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
      *<<entry.title>>*

      #v(design-highlights-top-margin)

      <<entry.authors|join(", ")>>

      #v(design-highlights-vertical-space-between-higlights)

      ((* if entry.doi -*))
      #link("<<entry.doi_url>>")[<<entry.doi>>]
      ((* elif entry.url -*))
      #link("<<entry.url>>")[<<entry.clean_url>>]
      ((*- endif -*))
      ((*- if (entry.doi or entry.url) and entry.journal *)) (((* endif -*))
      ((*- if entry.journal -*))
      <<entry.journal>>
      ((*- endif -*))
      ((*- if (entry.doi or entry.url) and entry.journal *)))((* endif *))
  ((* if entry.date_string *))
    ],
    right-content: [
      <<date_and_location_strings|join("\n\n")>>
    ],
  )
  ((* endif *)),
  breakable: design-entries-allow-page-break-in-entries,
)