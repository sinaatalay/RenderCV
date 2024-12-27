#show: rendercv.with(
  name: "<<cv.name>>",
  paper: "us-letter",
  page_numbering_style: "1 of 1",
  section-title-line-type: "partial",
  disable-last-updated-date: false,
  disable-connections-icon: false,
  last-updated-date-style: "Last updated in " + datetime.today().display(),
  last-updated-date-and-page-numbering-color: gray,
  disable-external-link-icon: false,
  font-size: 10pt,
  leading: 1.2em,
  section-title-font-scale: 1.2em,
  header-font-size: 30pt,
  header-font-weight: 700,
  header-color: blue,
  section-title-font-weight: 400,
  section-title-line-thickness: 0.5pt,
  margin-highlights-area-left-space: 0.5in,
  margin-highlights-area-space-between-bullet-and-highlight: 0.5em,
  margin-vertical-space-between-name-and-connections: 0.5cm,
  margin-vertical-space-between-connections-and-body: 0.5cm,
  margin-vertical-space-between-entries: 0.5cm,
  margin-section-title-bottom: 0.5cm,
  margin-page-top: 0.5in,
  margin-page-bottom: 0.5in,
  margin-page-left: 0.5in,
  margin-page-right: 0.5in,
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
