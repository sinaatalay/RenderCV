import functools
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline
from markdown_it.token import Token

from rendercv.schema.yaml_reader import TypstString

type RichTextNode = str | dict[str, Any]
type RichText = list[RichTextNode]


def math_rule(state: StateInline, silent: bool) -> bool:
    """Parse `$$...$$` as inline math.

    Why:
        CVs have used `$$...$$` for math since RenderCV 1. Single dollar signs
        are left alone, because CVs are full of prices like "$2M".

    Args:
        state: The inline parser state.
        silent: Whether to only check for a match without producing tokens.

    Returns:
        Whether math was found at the current position.
    """
    if not state.src.startswith("$$", state.pos):
        return False
    end = state.src.find("$$", state.pos + 2)
    if end == -1:
        return False
    if not silent:
        token = state.push("math_inline", "", 0)
        token.content = state.src[state.pos + 2 : end]
    state.pos = end + 2
    return True


@functools.cache
def get_markdown_parser() -> MarkdownIt:
    """Build the Markdown parser for CV text.

    Why:
        CV text is inline Markdown: bold, italic, links, code, and math, in
        paragraphs. Block syntax like headings and lists would clash with the
        CV's own structure, so only paragraphs are parsed as blocks.

    Returns:
        The parser.
    """
    parser = MarkdownIt("zero").enable(
        ["emphasis", "link", "backticks", "escape", "newline", "autolink", "entity"]
    )
    parser.inline.ruler.before("escape", "math", math_rule)
    return parser


def inline_tokens_to_rich_text(tokens: list[Token]) -> RichText:
    """Turn a paragraph's inline tokens into rich text nodes.

    Args:
        tokens: The children of an `inline` token.

    Returns:
        The rich text nodes.
    """
    root: RichText = []
    stack: list[RichText] = [root]
    for token in tokens:
        current = stack[-1]
        match token.type:
            case "text":
                # Emphasis leaves empty text tokens where its markers were:
                if token.content:
                    current.append(token.content)
            case "softbreak":
                current.append(" ")
            case "hardbreak":
                current.append({"linebreak": True})
            case "code_inline":
                current.append({"code": token.content})
            case "math_inline":
                current.append({"math": token.content})
            case "strong_open" | "em_open" | "link_open":
                children: RichText = []
                if token.type == "link_open":
                    url = str(token.attrGet("href") or "")
                    current.append({"link": {"url": url, "body": children}})
                else:
                    key = "strong" if token.type == "strong_open" else "emph"
                    current.append({key: children})
                stack.append(children)
            case "strong_close" | "em_close" | "link_close":
                stack.pop()
            case _:
                if token.content:
                    current.append(token.content)
    return merge_text(unwrap_empty_links(root))


def unwrap_empty_links(nodes: RichText) -> RichText:
    """Replace links without a URL, like `[text]()`, by their text.

    Args:
        nodes: Rich text nodes.

    Returns:
        The nodes without empty links.
    """
    result: RichText = []
    for node in nodes:
        if isinstance(node, dict) and "link" in node and not node["link"]["url"]:
            result.extend(unwrap_empty_links(node["link"]["body"]))
        elif isinstance(node, dict):
            key, value = next(iter(node.items()))
            if key in ("strong", "emph"):
                result.append({key: unwrap_empty_links(value)})
            elif key == "link":
                result.append(
                    {
                        "link": {
                            "url": value["url"],
                            "body": unwrap_empty_links(value["body"]),
                        }
                    }
                )
            else:
                result.append(node)
        else:
            result.append(node)
    return result


def merge_text(nodes: RichText) -> RichText:
    """Join neighboring strings into one.

    Args:
        nodes: Rich text nodes.

    Returns:
        The nodes with no two strings next to each other.
    """
    merged: RichText = []
    for node in nodes:
        if isinstance(node, str) and merged and isinstance(merged[-1], str):
            merged[-1] += node
        else:
            merged.append(node)
    return merged


def markdown_to_rich_text(text: str) -> RichText:
    """Turn CV text into rich text: formatting as data, never as code.

    Why:
        Typst gets the text's structure (bold, links, ...) as data and draws it
        with its own functions, so no character the user types can ever be read
        as Typst code. Text tagged `!typst` is the one exception: it is passed
        on as Typst markup on purpose.

    Example:
        ```py
        markdown_to_rich_text("Raised **$18M** for [Nexus](https://nexus.ai)")
        # ["Raised ", {"strong": ["$18M"]}, " for ",
        #  {"link": {"url": "https://nexus.ai", "body": ["Nexus"]}}]
        ```

    Args:
        text: Markdown text, or a `TypstString`.

    Returns:
        The rich text nodes.
    """
    if isinstance(text, TypstString):
        return [{"typst": str(text)}]
    nodes: RichText = []
    for token in get_markdown_parser().parse(text):
        if token.type == "inline":
            if nodes:
                nodes.append({"parbreak": True})
            nodes.extend(inline_tokens_to_rich_text(token.children or []))
    return nodes


def rich_text_to_plain_text(nodes: RichText) -> str:
    """Write rich text as plain text, dropping its formatting.

    Why:
        Some places only take plain text: the PDF's title and author, and
        output file names. A name written as `Jane **Doe**` should appear
        there as "Jane Doe".

    Example:
        ```py
        rich_text_to_plain_text(["Jane ", {"strong": ["Doe"]}])  # "Jane Doe"
        ```

    Args:
        nodes: Rich text nodes.

    Returns:
        The text without formatting.
    """
    parts: list[str] = []
    for node in nodes:
        if isinstance(node, str):
            parts.append(node)
            continue
        key, value = next(iter(node.items()))
        match key:
            case "strong" | "emph":
                parts.append(rich_text_to_plain_text(value))
            case "link":
                parts.append(rich_text_to_plain_text(value["body"]))
            case "code" | "math" | "typst":
                parts.append(str(value))
            case _:
                parts.append(" ")
    return "".join(parts)
