// Rich text: formatted text that arrives from RenderCV as data, never as code.
//
// RenderCV parses the Markdown in the YAML once and sends the result as a list
// of nodes. Plain strings are always shown literally, so characters like `#`,
// `$`, `@` or `*` in a CV can never break the document. Only a value the user
// explicitly tagged `!typst` in the YAML becomes a `typst` node that is
// evaluated as Typst markup.

/// Turns a list of rich text nodes into content.
///
/// Each node is a plain string, or a dictionary with exactly one of the keys
/// `strong`, `emph`, `link`, `code`, `math`, `typst`, `linebreak`, or
/// `parbreak`.
///
/// - nodes (array): The rich text nodes.
/// -> content
#let rich-nodes(nodes) = {
  nodes
    .map(node => {
      if type(node) == str {
        [#node]
      } else if "strong" in node {
        strong(rich-nodes(node.strong))
      } else if "emph" in node {
        emph(rich-nodes(node.emph))
      } else if "link" in node {
        link(node.link.url, rich-nodes(node.link.body))
      } else if "code" in node {
        raw(node.code)
      } else if "math" in node {
        // The source is kept as the alternative text, for accessibility and
        // for converting the CV back to Markdown:
        math.equation(eval(node.math, mode: "math").body, alt: node.math)
      } else if "typst" in node {
        eval(node.typst, mode: "markup")
      } else if "linebreak" in node {
        linebreak()
      } else if "parbreak" in node {
        parbreak()
      } else {
        panic("Unknown rich text node: " + repr(node))
      }
    })
    .join()
}

/// Turns rich text data into content.
///
/// Accepts the node list RenderCV sends, a plain string, content (returned as
/// is), or `none`.
///
/// - value (array, str, content, none): The rich text.
/// -> content, none
#let rich(value) = {
  if value == none {
    return none
  }
  if type(value) == content {
    return value
  }
  if type(value) == str {
    return [#value]
  }
  if value.len() == 0 {
    return none
  }
  rich-nodes(value)
}
