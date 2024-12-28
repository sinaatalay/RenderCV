#show: rendercv.with(
  name: "<<cv.name>>",
  paper: "<<design.page.size>>",
)


= <<cv.name>>


// Print connections:
#context {
  let connections = (
    connection("url", "text_url", icon: "icon"),
  )

  let list-of-connections = ()
  let m = 0
  let separator = h(0.5cm, weak: true) + " | " + h(0.5cm, weak: true)
  while (m <= connections.len() - 1) {
    let n = m + 1
    while (
      measure(connections.slice(m, n).join(separator)).width < page.width - 0.5in - 0.5in
    ) {
      n = n + 1
      if n > connections.len() {
        break
      }
    }
    list-of-connections.push(connections.slice(m, n - 1).join(separator))
    m = n
  }

  align(list-of-connections.join(linebreak()), center)
  v(1.33cm)
}
