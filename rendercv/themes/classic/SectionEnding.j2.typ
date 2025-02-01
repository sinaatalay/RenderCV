((* if entry_type in ["NumberedEntry", "ReversedNumberedEntry"] *))
  ((* if entry_type == "ReversedNumberedEntry" *))
  )
  #enum(
    numbering: n => [#{rev-enum-items.len() + 1 - n}.],
    ..rev-enum-items,
  )
  ((* endif *))
  ],
)
((* endif *))
