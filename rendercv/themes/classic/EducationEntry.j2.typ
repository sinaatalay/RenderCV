#block(
  ((* if design.entry_types.education_entry.degree_column_template and "\n\n" in second_column_template *))
  three-col-entry(
    left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
    left-content: [<<degree_column_template>>],
    middle-content: 
  ((* elif design.entry_types.education_entry.degree_column_template and "\n\n" not in second_column_template *))
  two-col-entry(
    left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
    right-column-width: 1fr,
    alignments: (left, left),
    left-content: [<<degree_column_template>>],
    right-content:
  ((* elif not design.entry_types.education_entry.degree_column_template and "\n\n" in second_column_template  *))
  two-col-entry(
    left-content:
  ((* endif *))
    [
      <<first_column_first_row_template>>
    ],
  ((* if "\n\n" in second_column_template *))
    right-content: [
      <<second_column_template>>
    ],
  ),
  ((* elif design.entry_types.education_entry.degree_column_template *))
  ),
  ((* endif *))
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
