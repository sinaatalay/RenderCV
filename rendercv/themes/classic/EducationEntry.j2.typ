((* if date_and_location_column_template and design.entry_types.education_entry.degree_column_template *))
// YES DATE, YES DEGREE
#three-col-entry(
  left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
  left-content: [<<degree_column_template>>],
  middle-content: [
    <<main_column_first_row_template>>
    ((* if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" *))
    #v(-design-text-leading)

    <<main_column_second_row_template>>
    ((* endif *))
  ],
  right-content: [
    <<date_and_location_column_template>>
  ],
)
((* if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n")) and main_column_second_row_template *))
#block(
  [
    <<main_column_second_row_template>>
  ],
  inset: (
    left: <<design.entry_types.education_entry.degree_column_width>> + <<design.entries.horizontal_space_between_columns>>,
  ),
)
((* endif *))
((* elif date_and_location_column_template and not design.entry_types.education_entry.degree_column_template *))
// YES DATE, NO DEGREE
#two-col-entry(
  left-content: [
    <<main_column_first_row_template>>
    ((* if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" *))
    #v(-design-text-leading)

    <<main_column_second_row_template>>
    ((* endif *))
  ],
  right-content: [
    <<date_and_location_column_template>>
  ],
)
  ((* if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv") *))
<<main_column_second_row_template>>
((* endif *))
((* elif not date_and_location_column_template and design.entry_types.education_entry.degree_column_template *))
// NO DATE, YES DEGREE
#two-col-entry(
  left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
  right-column-width: 1fr,
  alignments: (left, left),
  left-content: [
    <<degree_column_template>>
  ],
  right-content: [
    <<main_column_first_row_template>>
    ((* if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" *))
    #v(-design-text-leading)

    <<main_column_second_row_template>>
    ((* endif *))
  ],
)
((* if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n")) and main_column_second_row_template *))
#block(
  [
    <<main_column_second_row_template>>
  ],
  inset: (
    left: <<design.entry_types.education_entry.degree_column_width>> + <<design.entries.horizontal_space_between_columns>>,
  ),
)
((* endif *))
((* else *))
// NO DATE, NO DEGREE

<<main_column_first_row_template>>

<<main_column_second_row_template>>
((* endif *))