((* if section_title in design.show_timespan_in *))
    ((* set date_and_location_strings = [entry.location, entry.date_string, entry.time_span_string]|select("!=", "") *))
((* else *))
    ((* set date_and_location_strings = [entry.location, entry.date_string]|select("!=", "") *))
((* endif *))

((* if entry.date_string or entry.location *))
#two-col-entry(
  left-content: [
((* endif *))
    *<<entry.company>>*, <<entry.position>>
    
((* for item in entry.highlights *))
  ((* if loop.first *))
    #v(design-highlights-top-margin)
  ((* endif *))
    - <<item>>
((* endfor *))
((* if entry.date_string or entry.location *))
  ],
  right-content: [
    <<date_and_location_strings|join("\n\n")>>
  ],
)
((* endif *))
