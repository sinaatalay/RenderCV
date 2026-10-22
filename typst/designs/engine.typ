// The classic engine: the page layout all built-in designs share.
//
// `engine(options)` turns a dictionary of options into a design. The built-in
// designs are the engine with different default options and a few of their
// own entry looks. The option names follow RenderCV 2's `design:` fields, so a
// RenderCV 2 design maps onto them one to one.

#import "@preview/fontawesome:0.6.2": fa-icon
#import "../src/dates.typ": format-dates, format-date, format-time-span, month-abbreviation-and-year
#import "../src/values.typ": bullet-list
#import "../src/options.typ": merge-options

/// The options of the classic engine and their default values.
#let defaults = (
  page: (
    size: "us-letter",
    top_margin: 0.7in,
    bottom_margin: 0.7in,
    left_margin: 0.7in,
    right_margin: 0.7in,
    show_footer: true,
    show_top_note: true,
  ),
  colors: (
    body: rgb(0, 0, 0),
    name: rgb(0, 79, 144),
    headline: rgb(0, 79, 144),
    connections: rgb(0, 79, 144),
    section_titles: rgb(0, 79, 144),
    links: rgb(0, 79, 144),
    footer: rgb(128, 128, 128),
    top_note: rgb(128, 128, 128),
  ),
  typography: (
    line_spacing: 0.6em,
    alignment: "justified",
    date_and_location_column_alignment: right,
    font_family: (
      body: "Source Sans 3",
      name: "Source Sans 3",
      headline: "Source Sans 3",
      connections: "Source Sans 3",
      section_titles: "Source Sans 3",
    ),
    font_size: (
      body: 10pt,
      name: 30pt,
      headline: 10pt,
      connections: 10pt,
      section_titles: 1.4em,
    ),
    small_caps: (name: false, headline: false, connections: false, section_titles: false),
    bold: (name: true, headline: false, connections: false, section_titles: true),
  ),
  links: (underline: false, show_external_link_icon: false),
  header: (
    alignment: center,
    photo_width: 3.5cm,
    photo_position: "left",
    photo_space_left: 0.4cm,
    photo_space_right: 0.4cm,
    space_below_name: 0.7cm,
    space_below_headline: 0.7cm,
    space_below_connections: 0.7cm,
    connections: (
      phone_number_format: "national",
      hyperlink: true,
      show_icons: true,
      display_urls_instead_of_usernames: false,
      separator: "",
      space_between_connections: 0.5cm,
    ),
  ),
  section_titles: (
    type: "with_partial_line",
    line_thickness: 0.5pt,
    space_above: 0.5cm,
    space_below: 0.3cm,
  ),
  sections: (
    allow_page_break: true,
    space_between_regular_entries: 1.2em,
    space_between_text_based_entries: 0.3em,
    show_time_spans_in: ("experience",),
  ),
  entries: (
    date_and_location_width: 4.15cm,
    side_space: 0.2cm,
    space_between_columns: 0.1cm,
    allow_page_break: false,
    short_second_row: true,
    degree_width: 1cm,
    summary: (space_above: 0cm, space_left: 0cm),
    highlights: (
      bullet: "•",
      nested_bullet: "•",
      space_left: 0.15cm,
      space_above: 0cm,
      space_between_items: 0cm,
      space_between_bullet_and_text: 0.5em,
    ),
  ),
  templates: (
    /// `(info) => content`: the footer of every page.
    footer: info => context emph[#info.name -- #here().page()\/#counter(page).final().first()],
    /// `(info) => content`: the note at the top of the first page.
    top_note: info => emph[#info.locale.last_updated #(info.format-date)(info.current-date)],
    /// `(date, locale) => content`: how a date with a month is written.
    single_date: month-abbreviation-and-year,
    /// `(start, end) => content`: how a date range is written.
    date_range: (start, end) => [#start – #end],
    /// `(start, end, ctx) => content`: how long something lasted.
    time_span: (start, end, ctx) => format-time-span(start, end, ctx.locale, ctx.settings.current_date),
  ),
)

/// Section title types that center the title.
#let centered-section-title-types = (
  "centered_without_line",
  "centered_with_partial_line",
  "centered_with_centered_partial_line",
  "centered_with_full_line",
)

/// Accepts a single font name for `typography.font_family`, meaning all
/// elements use it.
#let expand-font-family(values) = {
  let typography = values.at("typography", default: none)
  if typography == none or type(typography.at("font_family", default: none)) != str {
    return values
  }
  let font = typography.font_family
  typography.font_family = (body: font, name: font, headline: font, connections: font, section_titles: font)
  values.typography = typography
  values
}

/// Resolves a design's options: its defaults with the user's values merged in.
///
/// - design-defaults (dictionary): Options to use instead of the engine's defaults.
/// - values (dictionary): The options the user set.
/// -> dictionary
#let resolve-options(design-defaults, values) = merge-options(
  merge-options(defaults, expand-font-family(design-defaults)),
  expand-font-family(values),
)

/// Builds a design from resolved options.
///
/// Entry looks in `entries` replace the engine's own looks, by entry type name.
///
/// - o (dictionary): Resolved options.
/// - name (str): The design's name.
/// - entries (function): `(o, parts) => dictionary` of entry looks, given the
///   options and the engine's building blocks.
/// -> dictionary
#let engine(o, name: "classic", entries: (o, parts) => (:)) = {
  let (justify, hyphenate) = (
    "justified": (true, true),
    "left": (false, false),
    "justified-with-no-hyphenation": (true, false),
  ).at(o.typography.alignment)
  let is-moderncv = o.section_titles.type == "moderncv"
  let regular-entry-spacing = o.sections.space_between_regular_entries + o.typography.line_spacing
  let text-entry-spacing = o.sections.space_between_text_based_entries + o.typography.line_spacing

  let is-rtl(ctx) = ctx.locale.direction == "rtl"
  let start-align(ctx) = if is-rtl(ctx) { right } else { left }
  let end-align(ctx) = if is-rtl(ctx) { left } else { right }
  // Maps logical start/end insets to physical left/right.
  let directional-inset(ctx, start: 0cm, end: 0cm) = if is-rtl(ctx) {
    (left: end, right: start)
  } else {
    (left: start, right: end)
  }

  // Writes the date of an entry, with how long it lasted in sections listed in
  // `sections.show_time_spans_in`.
  let entry-dates(it, ctx) = {
    let when = format-dates(
      ctx.locale,
      date: it.at("date", default: none),
      start: it.at("start_date", default: none),
      end: it.at("end_date", default: none),
      format: o.templates.single_date,
      range: o.templates.date_range,
    )
    let section-key = if ctx.section.parent == none { ctx.section.key } else { ctx.section.parent.key }
    let start = it.at("start_date", default: none)
    if (
      it.at("date", default: none) == none
        and start != none
        and section-key in o.sections.show_time_spans_in
    ) {
      let span = (o.templates.time_span)(start, it.at("end_date", default: none), ctx)
      if span != none and span != "" {
        return (when, span)
      }
    }
    (when,)
  }

  // Lines of an entry column, skipping empty ones.
  let lines(..items) = items.pos().filter(item => item != none and item != [] and item != "")
  // Stacks lines as separate paragraphs.
  let stack-lines(items) = if items.len() == 0 { none } else { items.join(parbreak()) }

  // The summary of an entry, set off a little from the lines above it.
  let summary-block(summary, ctx) = {
    if summary == none {
      return none
    }
    block(
      summary,
      inset: directional-inset(ctx, start: o.entries.summary.space_left),
      above: o.entries.summary.space_above + o.typography.line_spacing,
    )
  }

  // Bullets styled with the design's highlight options.
  let highlights-list(highlights) = {
    if highlights == none or highlights.len() == 0 {
      return none
    }
    set list(
      marker: (o.entries.highlights.bullet, o.entries.highlights.nested_bullet),
      indent: o.entries.highlights.space_left,
      spacing: o.entries.highlights.space_between_items + o.typography.line_spacing,
      body-indent: o.entries.highlights.space_between_bullet_and_text,
    )
    block(above: o.entries.highlights.space_above + o.typography.line_spacing, bullet-list(highlights))
  }

  // The body below an entry's title: summary, then highlights.
  let entry-body(it, ctx) = (
    summary-block(it.at("summary", default: none), ctx),
    highlights-list(it.at("highlights", default: none)),
  )
    .filter(part => part != none)
    .join()

  // An entry with a main column and a date and location column. `main` and
  // `aside` are arrays of lines. With `entries.short_second_row`, the whole
  // main column sits next to the dates; otherwise only as many main lines as
  // the date column has, and the rest spans the full width below.
  let regular-entry(ctx, main, aside, body: none, degree: none) = {
    set par(spacing: o.typography.line_spacing, leading: o.typography.line_spacing, justify: justify)
    let main = if type(main) == array { lines(..main) } else { lines(main) }
    let aside = if type(aside) == array { lines(..aside) } else { lines(aside) }
    let with-body(main-lines) = {
      let top = stack-lines(main-lines)
      if body == none { top } else if top == none { body } else { [#top#parbreak()#body] }
    }
    let with-degree(content) = if degree == none {
      content
    } else {
      grid(
        columns: (o.entries.degree_width, 1fr),
        column-gutter: o.entries.space_between_columns,
        align: (start-align(ctx), auto),
        degree, content,
      )
    }
    let degree-indent = if degree == none { 0cm } else { o.entries.degree_width + o.entries.space_between_columns }
    let first-row-length = calc.max(1, aside.len())
    block(
      {
        if is-moderncv {
          grid(
            columns: (o.entries.date_and_location_width, 1fr),
            column-gutter: o.entries.space_between_columns,
            align: (o.typography.date_and_location_column_alignment, start-align(ctx)),
            stack-lines(aside), with-degree(with-body(main)),
          )
        } else if o.entries.short_second_row or (body == none and main.len() <= first-row-length) {
          grid(
            columns: (1fr, o.entries.date_and_location_width),
            column-gutter: o.entries.space_between_columns,
            align: (start-align(ctx), o.typography.date_and_location_column_alignment),
            with-degree(with-body(main)), stack-lines(aside),
          )
        } else {
          grid(
            columns: (1fr, o.entries.date_and_location_width),
            column-gutter: o.entries.space_between_columns,
            align: (start-align(ctx), o.typography.date_and_location_column_alignment),
            with-degree(stack-lines(main.slice(0, calc.min(first-row-length, main.len())))),
            stack-lines(aside),
          )
          let second-row = with-body(main.slice(calc.min(first-row-length, main.len())))
          set align(start-align(ctx))
          if second-row == none {
            // Nothing below the first row.
          } else if degree == none {
            // Placed directly, so the summary and highlights keep their own
            // spacing above them:
            second-row
          } else {
            block(second-row, inset: directional-inset(ctx, start: degree-indent), above: o.typography.line_spacing)
          }
        }
      },
      breakable: o.entries.allow_page_break,
      below: regular-entry-spacing,
      inset: (left: o.entries.side_space, right: o.entries.side_space),
      width: 100%,
    )
  }

  // A text-based entry: a paragraph, a one-line entry, or a list item.
  let text-entry(ctx, content) = {
    let start-space = o.entries.side_space
    if is-moderncv {
      start-space += o.entries.date_and_location_width + o.entries.space_between_columns
    }
    set par(spacing: text-entry-spacing, leading: o.typography.line_spacing, justify: justify)
    set align(start-align(ctx))
    set enum(spacing: text-entry-spacing)
    set list(
      marker: (o.entries.highlights.bullet, o.entries.highlights.nested_bullet),
      indent: 0cm,
      spacing: text-entry-spacing,
      body-indent: o.entries.highlights.space_between_bullet_and_text,
    )
    block(
      content,
      breakable: o.entries.allow_page_break,
      below: text-entry-spacing,
      inset: directional-inset(ctx, start: start-space, end: o.entries.side_space),
      width: 100%,
    )
  }

  // Writes "PhD in Computer Science" with the locale's phrase.
  let degree-with-area(it, ctx) = if it.degree == none {
    it.area
  } else {
    eval(ctx.locale.phrases.degree_with_area, mode: "markup", scope: (degree: it.degree, area: it.area))
  }

  // A publication's link: its DOI, or else its URL.
  let publication-link(it) = if it.doi != none {
    link("https://doi.org/" + it.doi, it.doi)
  } else if it.url != none {
    link(it.url, it.url.replace(regex("^https?://(www\\.)?"), "").trim("/", at: end))
  }

  // " -- Location" after a title, if there is a location.
  let dash-location(location) = if location != none [ -- #location]

  // The building blocks designs use to write their own entry looks.
  let parts = (
    regular-entry: regular-entry,
    text-entry: text-entry,
    entry-dates: entry-dates,
    entry-body: entry-body,
    summary-block: summary-block,
    lines: lines,
    degree-with-area: degree-with-area,
    publication-link: publication-link,
    dash-location: dash-location,
  )

  let engine-entries = (
    normal: (it, ctx) => regular-entry(
      ctx,
      strong(it.name),
      (it.location, ..entry-dates(it, ctx)),
      body: entry-body(it, ctx),
    ),
    experience: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.company), #it.position],
      (it.location, ..entry-dates(it, ctx)),
      body: entry-body(it, ctx),
    ),
    education: (it, ctx) => regular-entry(
      ctx,
      [#strong(it.institution), #it.area],
      (it.location, ..entry-dates(it, ctx)),
      body: entry-body(it, ctx),
      degree: if it.degree != none { strong(it.degree) },
    ),
    publication: (it, ctx) => {
      let venue = (publication-link(it), if it.journal != none [(#it.journal)]).filter(part => part != none)
      regular-entry(
        ctx,
        (
          strong(it.title),
          summary-block(it.summary, ctx),
          it.authors.join(", "),
          if venue.len() > 0 { venue.join(" ") },
        ),
        entry-dates(it, ctx),
      )
    },
    one_line: (it, ctx) => text-entry(ctx, par[#strong[#it.label:] #it.details]),
    bullet: (it, ctx) => text-entry(ctx, list(it.bullet)),
    numbered: (it, ctx) => text-entry(ctx, enum(enum.item(ctx.index, it.number))),
    reversed_numbered: (it, ctx) => text-entry(ctx, enum(enum.item(ctx.count - ctx.index + 1, it.reversed_number))),
    paragraph: (it, ctx) => text-entry(ctx, par(it.text)),
  )

  // The header: photo, name, headline, and connections.
  let headline-block(headline, ctx) = {
    set text(
      fill: o.colors.headline,
      font: o.typography.font_family.headline,
      size: o.typography.font_size.headline,
      weight: if o.typography.bold.headline { 700 } else { 400 },
    )
    set align(o.header.alignment)
    block(if o.typography.small_caps.headline { smallcaps(headline) } else { headline }, width: 100%)
    v(o.header.space_below_headline, weak: true)
  }

  let connection-body(connection) = {
    let options = o.header.connections
    let body = if connection.kind == "phone" and connection.at("phone", default: none) != none {
      [#connection.phone.at(lower(options.phone_number_format))]
    } else if options.display_urls_instead_of_usernames and connection.at("url_text", default: none) != none {
      [#connection.url_text]
    } else {
      connection.text
    }
    if options.show_icons {
      // The box isolates the text, so the paragraph direction decides the order.
      body = [#fa-icon(connection.icon, size: 0.9em) #h(0.05cm) #box(body)]
    }
    if options.hyperlink and connection.url != none {
      body = link(connection.url, body)
    }
    body
  }

  let connections-block(connections, ctx) = {
    let options = o.header.connections
    set par(spacing: 0pt, leading: o.typography.line_spacing * 1.7, justify: false)
    set text(
      fill: o.colors.connections,
      font: o.typography.font_family.connections,
      size: o.typography.font_size.connections,
      weight: if o.typography.bold.connections { 700 } else { 400 },
    )
    let separator = (
      h(options.space_between_connections / 2, weak: true)
        + options.separator
        + h(options.space_between_connections / 2, weak: true)
    )
    if connections.len() > 0 {
      set align(o.header.alignment)
      box(
        layout(size => {
          let separator-width = measure(options.separator).width + options.space_between_connections
          let line-width = 0cm
          for connection in connections {
            let body = connection-body(connection)
            let body = if o.typography.small_caps.connections { smallcaps(body) } else { body }
            let body-width = measure(body).width
            // Start a new line if this connection doesn't fit on the current one.
            if line-width + body-width + separator-width > size.width and line-width > 0cm {
              linebreak()
              line-width = 0cm
            }
            if line-width > 0cm {
              separator
            }
            box(body, width: auto)
            line-width += body-width + if line-width > 0cm { separator-width } else { 0cm }
          }
        }),
        width: 100%,
      )
    }
    v(o.header.space_below_connections - o.section_titles.space_above)
  }

  let header(h, ctx) = {
    let photo = if h.photo != none {
      pad(
        left: o.header.photo_space_left,
        right: o.header.photo_space_right,
        image(h.photo, width: o.header.photo_width),
      )
    }
    let details = {
      if h.name != none {
        heading(level: 1, h.name)
      }
      if h.headline != none {
        headline-block(h.headline, ctx)
      }
      connections-block(h.connections, ctx)
    }
    if photo == none {
      details
    } else if o.header.photo_position == "left" {
      grid(columns: (auto, 1fr), column-gutter: 0cm, align: horizon + left, photo, details)
    } else {
      grid(columns: (1fr, auto), column-gutter: 0cm, align: horizon + left, details, photo)
    }
  }

  // A section: its title, then its entries.
  let section(s, body, ctx) = {
    if s.level > 1 {
      // A subsection.
      block(
        above: o.section_titles.space_above / 2,
        below: o.section_titles.space_below,
        sticky: true,
        inset: directional-inset(ctx, start: o.entries.side_space),
        text(weight: 700, fill: o.colors.section_titles, s.title),
      )
      body
      return
    }
    heading(level: 2, s.title)
    block(breakable: o.sections.allow_page_break, {
      show link: set text(fill: o.colors.links)
      show link: it => {
        let styled = if o.links.underline { underline(it) } else { it }
        if not o.links.show_external_link_icon {
          return styled
        }
        // A zero-height box keeps the icon from changing the line height; the
        // box around the link isolates it, so the paragraph direction decides
        // which side the icon goes on.
        let icon = fa-icon("external-link", size: 0.65em)
        [#box(styled)#h(o.typography.font_size.body / 4)#box(
            width: measure(icon).width,
            height: 0pt,
            baseline: 0pt,
            place(dy: -0.75em, icon),
          )]
      }
      body
    })
  }

  let document-setup(body, info) = {
    let info = info + (format-date: date => format-date(date, info.locale, format: o.templates.single_date))
    let is-rtl = info.locale.direction == "rtl"
    let start-align = if is-rtl { right } else { left }
    let end-align = if is-rtl { left } else { right }

    set document(title: info.title, author: info.author, keywords: info.keywords)
    set page(
      margin: (
        top: o.page.top_margin,
        bottom: o.page.bottom_margin,
        left: o.page.left_margin,
        right: o.page.right_margin,
      ),
      paper: o.page.size,
      footer: if o.page.show_footer {
        text(fill: o.colors.footer, size: 0.9em, align(center, (o.templates.footer)(info)))
      },
      footer-descent: 0% - 0.6em + o.page.bottom_margin / 2,
    )
    set text(
      font: o.typography.font_family.body,
      size: o.typography.font_size.body,
      lang: info.locale.iso_code,
      dir: if is-rtl { rtl } else { ltr },
      hyphenate: hyphenate,
      fill: o.colors.body,
    )
    set par(spacing: 0cm)

    // The name.
    show heading.where(level: 1): it => {
      set par(spacing: 0pt)
      set align(o.header.alignment)
      set text(
        font: o.typography.font_family.name,
        size: o.typography.font_size.name,
        fill: o.colors.name,
        weight: if o.typography.bold.name { 700 } else { 400 },
      )
      block(if o.typography.small_caps.name { smallcaps(it.body) } else { it.body })
      v(o.header.space_below_name, weak: true)
    }

    // Section titles.
    show heading.where(level: 2): it => {
      let type = o.section_titles.type
      let line = box(width: 1fr, height: o.section_titles.line_thickness, fill: o.colors.section_titles)
      set align(if type in centered-section-title-types { center } else { start-align })
      // Undo the size Typst gives second-level headings by default, so
      // `font_size.section_titles` is relative to the body text:
      set text(size: 1em / 1.2)
      set text(
        font: o.typography.font_family.section_titles,
        size: o.typography.font_size.section_titles,
        weight: if o.typography.bold.section_titles { 700 } else { 400 },
        fill: o.colors.section_titles,
      )
      let title = if o.typography.small_caps.section_titles { smallcaps(it.body) } else { it.body }
      v(o.section_titles.space_above, weak: true)
      block(breakable: false, sticky: true, width: 100%, {
        if type == "moderncv" {
          grid(
            columns: (o.entries.date_and_location_width + o.entries.side_space, 1fr),
            column-gutter: o.entries.space_between_columns,
            align: (end-align, start-align),
            align(horizon, line), title,
          )
        } else if type == "centered_with_partial_line" {
          grid(
            columns: (1fr, auto, 1fr),
            align: (bottom, center + bottom, bottom),
            column-gutter: 0.3em,
            line, title, line,
          )
        } else if type == "centered_with_centered_partial_line" {
          grid(
            columns: (1fr, auto, 1fr),
            align: (horizon, center, horizon),
            column-gutter: 0.3em,
            line, title, line,
          )
        } else if type in ("centered_with_full_line", "with_full_line") {
          title
          v(o.typography.font_size.body * 0.3)
          line
        } else if type == "with_partial_line" {
          [#title #line]
        } else {
          title
        }
      })
      v(o.section_titles.space_below - 0.5em)
    }

    // The note at the top of the first page.
    if o.page.show_top_note {
      place(
        top + end-align,
        dy: -o.page.top_margin / 2,
        dx: if is-rtl { o.entries.side_space } else { -o.entries.side_space },
        text(fill: o.colors.top_note, size: 0.9em, (o.templates.top_note)(info)),
      )
    }
    body
  }

  (
    name: name,
    options: o,
    document: document-setup,
    header: header,
    section: section,
    entries: engine-entries + entries(o, parts),
    // The building blocks of the looks above, for looks users add:
    parts: parts,
  )
}
