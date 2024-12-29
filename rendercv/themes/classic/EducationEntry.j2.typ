((* if section_title in design.theme_specific.show_timespan_in *))
    ((* set date_and_location_strings = [entry.location, entry.date_string, entry.time_span_string]|select("!=", "") *))
((* else *))
    ((* set date_and_location_strings = [entry.location, entry.date_string]|select("!=", "") *))
((* endif *))
#block(
  three-col-entry(
    left-column-width: design-theme-specific-education-degree-width,
    left-content: [*<<entry.degree>>*],
    middle-content: [
      *<<entry.institution>>*, <<entry.area>>
      
  ((* for item in entry.highlights *))
    ((* if loop.first *))
      #v(design-highlights-top-margin)
    ((* endif *))
      - <<item>>
  ((* endfor *))
    ],
    right-content: [
      <<date_and_location_strings|join("\n\n")>>
    ],
  ),
  breakable: design-entries-allow-page-break-in-entries,
)
