import itertools
import re
from xml.etree.ElementTree import Element

import markdown
import markdown.core

from .string_processor import clean_url


def to_typst_string(elem: Element) -> str:
    """Recursively convert XML Element tree to Typst markup string.

    Why:
        Python Markdown library outputs XML Element tree. Typst requires its
        own markup syntax for bold, italic, links, etc. Recursive traversal
        converts entire element tree including nested formatting.

    Args:
        elem: XML Element from Markdown parser.

    Returns:
        Typst-formatted string.
    """
    result = []

    # Handle the element's text content
    if elem.text:
        result.append(escape_typst_characters(elem.text))

    # Process child elements
    for child in elem:
        match child.tag:
            case "strong":
                # Bold: **text** -> #strong[text]
                inner = to_typst_string(child)
                child_content = f"#strong[{inner}]"

            case "em":
                # Italic: *text* -> #emph[text]
                inner = to_typst_string(child)
                child_content = f"#emph[{inner}]"

            case "code":
                # Inline code: `text` -> `text`
                # Code content is already escaped by the parser
                child_content = f"`{child.text}`"

            case "a":
                # Link: [text](url) -> #link("url")[text]
                href = child.get("href") if child.get("href") else "https://example.com"
                inner = to_typst_string(child)
                child_content = f'#link("{href}")[{inner}]'

            case "div":
                child_content = (
                    "#summary["
                    + to_typst_string(child).strip("\n").replace("\n", " \\ ")
                    + "]"
                )

            case _:
                if getattr(child, "attrib", {}).get("class") == "admonition-title":
                    continue
                child_content = to_typst_string(child)

        result.append(child_content)

        # Handle tail text (text after the closing tag of child)
        if child.tail:
            result.append(escape_typst_characters(child.tail))

    return "".join(result)


def to_plain_text_string(elem: Element) -> str:
    """Recursively convert XML Element tree to a plain text string.

    Why:
        Plain text output must not contain any markup. Formatting elements are
        reduced to their inner text, and links keep their URL in parentheses
        when it adds information over the link text.

    Args:
        elem: XML Element from Markdown parser.

    Returns:
        Plain text string.
    """
    result = []

    if elem.text:
        result.append(elem.text)

    for child in elem:
        match child.tag:
            case "code":
                child_content = child.text or ""

            case "a":
                # Link: [text](url) -> text (url), or just text when the URL
                # adds no information (e.g. mailto: links, bare URLs)
                href = child.get("href") or ""
                inner = to_plain_text_string(child)
                href_body = href.removeprefix("mailto:").removeprefix("tel:")
                if not inner:
                    child_content = href_body
                elif not href_body or inner in {href_body, clean_url(href)}:
                    child_content = inner
                else:
                    child_content = f"{inner} ({href_body})"

            case _:
                if getattr(child, "attrib", {}).get("class") == "admonition-title":
                    continue
                child_content = to_plain_text_string(child)

        result.append(child_content)

        if child.tail:
            result.append(child.tail)

    return "".join(result)


typst_command_pattern = re.compile(r"#([A-Za-z][^\s()\[]*)(\([^)]*\))?(\[[^\]]*\])?")
math_pattern = re.compile(r"(\$\$.*?\$\$)")


def escape_typst_characters(string: str) -> str:
    """Escape Typst special characters while preserving Typst commands and math.

    Why:
        User content may contain Typst special characters like `#`, `$`, `[` that
        would break compilation. Escaping prevents interpretation as commands.
        Existing Typst commands and math must remain unescaped.

    Args:
        string: Text to escape.

    Returns:
        Escaped string safe for Typst.
    """
    if string == "\n":
        return string

    # Find all the Typst commands, and keep them separate so that nothing is escaped
    # inside the commands.
    typst_command_mapping = {}
    for i, match in enumerate(
        itertools.chain(
            math_pattern.finditer(string),
            typst_command_pattern.finditer(string),
        )
    ):
        dummy_name = f"RENDERCVTYPSTCOMMANDORMATH{i}"
        typst_command_mapping[dummy_name] = match.group(0)
        string = string.replace(typst_command_mapping[dummy_name], dummy_name)
        typst_command_mapping[dummy_name] = typst_command_mapping[dummy_name].replace(
            "$$", "$"
        )

    # Add the tail after the last match
    escape_dictionary = {
        "[": "\\[",
        "]": "\\]",
        "\\": "\\\\",
        '"': '\\"',
        "#": "\\#",
        "$": "\\$",
        "@": "\\@",
        "%": "\\%",
        "~": "\\~",
        "_": "\\_",
        "/": "\\/",
        ">": "\\>",
        "<": "\\<",
    }

    string = string.translate(str.maketrans(escape_dictionary))

    # string.translate() only supports single-character replacements, so we need to
    # handle the longer replacements separately.
    longer_escape_dictionary = {
        "* ": "#sym.ast.basic ",
        "*": "#sym.ast.basic#h(0pt, weak: true) ",
    }
    for key, value in longer_escape_dictionary.items():
        string = string.replace(key, value)

    # Replace the dummy names with the full Typst commands
    for dummy_name, full_command in typst_command_mapping.items():
        string = string.replace(dummy_name, full_command)

    return string


# Create a Markdown instance
md = markdown.core.Markdown(extensions=["admonition"])
md.output_formats["typst"] = to_typst_string  # pyright: ignore[reportArgumentType]
md.set_output_format("typst")  # pyright: ignore[reportArgumentType]
md.parser.blockprocessors.deregister("hashheader")
md.parser.blockprocessors.deregister("setextheader")
md.parser.blockprocessors.deregister("olist")
md.parser.blockprocessors.deregister("ulist")
md.parser.blockprocessors.deregister("quote")
md.stripTopLevelTags = False


def markdown_to_typst(markdown_string: str) -> str:
    """Convert Markdown string to Typst markup.

    Why:
        Users write content in Markdown for readability. Typst compilation
        requires Typst markup. Lines are processed independently to prevent
        emphasis markers on adjacent lines from interacting in the Markdown
        parser (single-newline-separated lines form one paragraph in Markdown,
        causing cross-line marker interference). Admonition blocks are kept
        together since they span multiple lines by design.

    Args:
        markdown_string: Markdown content.

    Returns:
        Typst-formatted string.
    """
    lines = markdown_string.split("\n")
    result_parts: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("!!!"):
            # Admonition block: collect the !!! line + all following indented lines
            block = [lines[i]]
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i])
                i += 1
            md.reset()
            result_parts.append(md.convert("\n".join(block)))
        else:
            md.reset()
            result_parts.append(md.convert(lines[i]))
            i += 1
    return "\n".join(result_parts)


# Create a Markdown instance for plain text output
md_plain = markdown.core.Markdown(extensions=["admonition"])
md_plain.output_formats["plaintext"] = to_plain_text_string  # pyright: ignore[reportArgumentType]
md_plain.set_output_format("plaintext")  # pyright: ignore[reportArgumentType]
md_plain.parser.blockprocessors.deregister("hashheader")
md_plain.parser.blockprocessors.deregister("setextheader")
md_plain.parser.blockprocessors.deregister("olist")
md_plain.parser.blockprocessors.deregister("ulist")
md_plain.parser.blockprocessors.deregister("quote")
md_plain.stripTopLevelTags = False


def markdown_to_plain_text(markdown_string: str) -> str:
    """Convert Markdown string to plain text.

    Why:
        Plain text output must be readable without any renderer. Lines are
        processed independently for the same reason as in `markdown_to_typst`,
        and admonition blocks are kept together since they span multiple lines
        by design.

    Args:
        markdown_string: Markdown content.

    Returns:
        Plain text string.
    """
    lines = markdown_string.split("\n")
    result_parts: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("!!!"):
            # Admonition block: collect the !!! line + all following indented lines
            block = [lines[i]]
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i])
                i += 1
            md_plain.reset()
            result_parts.append(md_plain.convert("\n".join(block)))
        else:
            md_plain.reset()
            result_parts.append(md_plain.convert(lines[i]))
            i += 1
    return "\n".join(result_parts)


def markdown_to_html(markdown_string: str) -> str:
    """Convert Markdown string to HTML using python-markdown library.

    Args:
        markdown_string: Markdown content.

    Returns:
        HTML-formatted string.
    """
    return markdown.markdown(markdown_string)
