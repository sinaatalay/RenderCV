// Markdown and plain text: reading a rendered document back as text.
//
// RenderCV draws the CV once with semantic Typst (headings, paragraphs, lists,
// links, strong and emphasized text) and converts that content to Markdown or
// plain text here. So the text outputs come from the same entry type looks as
// the PDF, instead of from separate templates.

/// Escapes characters Markdown would otherwise interpret.
#let escape-markdown(text) = text.replace(regex("[\\\\`*_\\[\\]]"), m => "\\" + m.text)

/// Converts content to Markdown.
///
/// - it (content, str, none): The content.
/// - plain (bool): Whether to write plain text instead of Markdown.
/// - indent (str): The indentation of the current list level.
/// -> str
#let to-markdown(it, plain: false, indent: "") = {
  if it == none {
    return ""
  }
  if type(it) == str {
    return if plain { it } else { escape-markdown(it) }
  }
  if type(it) != content {
    return str(it)
  }
  let convert = child => to-markdown(child, plain: plain, indent: indent)
  let name = repr(it.func())
  if name == "text" {
    return if plain { it.text } else { escape-markdown(it.text) }
  }
  if name == "space" {
    return " "
  }
  if name == "linebreak" {
    return if plain { "\n" + indent } else { "  \n" + indent }
  }
  if name == "parbreak" {
    return "\n\n"
  }
  if name == "smartquote" {
    return if it.double { "\"" } else { "'" }
  }
  if name == "strong" {
    return if plain { convert(it.body) } else { "**" + convert(it.body) + "**" }
  }
  if name == "emph" {
    return if plain { convert(it.body) } else { "*" + convert(it.body) + "*" }
  }
  if name == "raw" {
    return if plain { it.text } else { "`" + it.text + "`" }
  }
  if name == "equation" and it.at("alt", default: none) != none {
    return if plain { it.alt } else { "$$" + it.alt + "$$" }
  }
  if name == "link" {
    let body = convert(it.body)
    let destination = if type(it.dest) == str { it.dest } else { none }
    if plain or destination == none {
      return body
    }
    return "[" + body + "](" + destination + ")"
  }
  if name == "par" {
    return "\n\n" + convert(it.body) + "\n\n"
  }
  if name == "heading" {
    let body = convert(it.body)
    // Headings written as `= Title` have a depth but no level yet:
    let level = if it.has("level") and it.level != auto { it.level } else { it.at("depth", default: 1) }
    return "\n\n" + (if plain { body } else { "#" * level + " " + body }) + "\n\n"
  }
  if it.func() == list.item or it.func() == enum.item {
    // Items written in markup, like `- item`, aren't in a list yet:
    let number = it.at("number", default: none)
    let marker = if it.func() == list.item { "- " } else { str(if number == none { 1 } else { number }) + ". " }
    return "\n" + indent + marker + to-markdown(it.body, plain: plain, indent: indent + "  ").trim()
  }
  if name == "list" or name == "enum" {
    let lines = it
      .children
      .enumerate()
      .map(((index, item)) => {
        let marker = if name == "list" {
          "- "
        } else {
          let number = if item.has("number") and item.number != none { item.number } else { index + 1 }
          str(number) + ". "
        }
        let body = to-markdown(item.body, plain: plain, indent: indent + "  ")
        indent + marker + body.trim()
      })
    return "\n\n" + lines.join("\n", default: "") + "\n\n"
  }
  if name in ("metadata", "place", "v", "image", "context", "counter-update", "state-update", "pagebreak") {
    return ""
  }
  if name == "h" {
    return " "
  }
  if name == "sequence" {
    return it.children.map(convert).join(default: "")
  }
  if name == "styled" {
    return convert(it.child)
  }
  if name in ("grid", "table") {
    return it.children.map(convert).map(text => text.trim()).filter(text => text != "").join("\n\n", default: "")
  }
  if it.has("body") {
    return convert(it.body)
  }
  if it.has("child") {
    return convert(it.child)
  }
  if it.has("children") {
    return it.children.map(convert).join(default: "")
  }
  if it.has("text") {
    return it.text
  }
  ""
}

/// Converts content to tidy Markdown: at most one blank line between blocks
/// and no trailing spaces.
///
/// - it (content): The content.
/// - plain (bool): Whether to write plain text instead of Markdown.
/// -> str
#let to-markdown-document(it, plain: false) = {
  let text = to-markdown(it, plain: plain)
  let text = text.replace(regex("[ \\t]+\\n"), m => if m.text.starts-with("  ") and not plain { "  \n" } else { "\n" })
  let text = text.replace(regex("\\n{3,}"), "\n\n")
  text.trim() + "\n"
}
