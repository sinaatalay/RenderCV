((* if section_title in design.show_timespan_in *))
    ((* set date_and_location_strings = [entry.location, entry.date_string, entry.time_span_string]|select("!=", "") *))
((* else *))
    ((* set date_and_location_strings = [entry.location, entry.date_string]|select("!=", "") *))
((* endif *))

((* if entry.date_string *))
#two-col-entry(
  left-content: [
((* endif *))
    *<<entry.title>>*

    <<entry.authors|join(", ")>>

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
((* endif *))
