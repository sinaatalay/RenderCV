#block(
  ((* if degree_column *))
  three-col-entry(
    left-column-width: 1cm,
    left-content: [*<<entry.degree>>*],
    middle-content: [<<first_column>>],
  ((* else *))
  two-col-entry(
    left-content: [
      <<first_column>>
    ],
  ((* endif *))
    right-content: [
      <<second_column>>
    ],
  ),
  breakable: design-entries-allow-page-break-in-entries,
)
