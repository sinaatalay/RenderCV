((* if section_title in design.show_timespan_in *))
    ((* set date_and_location_strings = [entry.location, entry.date_string, entry.time_span_string]|select("!=", "") *))
((* else *))
    ((* set date_and_location_strings = [entry.location, entry.date_string]|select("!=", "") *))
((* endif *))

#three-col-entry(
  left-column-width: 1.5cm,
  right-column-width: 2.5cm,
  left-content: [*<<entry.degree>>*],
  middle-content: [
    *<<entry.institution>>*, <<entry.area>>
    
((* for item in entry.highlights *))
    - <<item>>
((* endfor *))
  ],
  right-content: [
    <<date_and_location_strings|join("\n\n")>>
  ],
)
