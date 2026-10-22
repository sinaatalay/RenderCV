import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from markdown_it.token import Token

from rendercv.renderer.rich_text import (
    RichText,
    get_markdown_parser,
    inline_tokens_to_rich_text,
    markdown_to_rich_text,
    merge_text,
    rich_text_to_plain_text,
    unwrap_empty_links,
)
from rendercv.schema.yaml_reader import TypstString


class TestMarkdownToRichText:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("plain text", ["plain text"]),
            ("**bold**", [{"strong": ["bold"]}]),
            ("__bold__", [{"strong": ["bold"]}]),
            ("*italic*", [{"emph": ["italic"]}]),
            ("_italic_", [{"emph": ["italic"]}]),
            ("***both***", [{"emph": [{"strong": ["both"]}]}]),
            (
                "a **b *c* d** e",
                ["a ", {"strong": ["b ", {"emph": ["c"]}, " d"]}, " e"],
            ),
            (
                "[RenderCV](https://rendercv.com)",
                [{"link": {"url": "https://rendercv.com", "body": ["RenderCV"]}}],
            ),
            (
                '[title](https://x.com "a title")',
                [{"link": {"url": "https://x.com", "body": ["title"]}}],
            ),
            (
                "[**bold** link](https://x.com)",
                [
                    {
                        "link": {
                            "url": "https://x.com",
                            "body": [{"strong": ["bold"]}, " link"],
                        }
                    }
                ],
            ),
            ("`code`", [{"code": "code"}]),
            ("`a ** b`", [{"code": "a ** b"}]),
            ("`` a`b ``", [{"code": "a`b"}]),
            ("$$x^2$$", [{"math": "x^2"}]),
            (
                "Energy $$E = m c^2$$ here",
                ["Energy ", {"math": "E = m c^2"}, " here"],
            ),
            ("$$a$$$$b$$", [{"math": "a"}, {"math": "b"}]),
            ("\\*not italic\\*", ["*not italic*"]),
            ("\\[not a link\\]", ["[not a link]"]),
            ("\\$\\$", ["$$"]),
            (
                "<https://example.com>",
                [
                    {
                        "link": {
                            "url": "https://example.com",
                            "body": ["https://example.com"],
                        }
                    }
                ],
            ),
            (
                "<john@doe.com>",
                [{"link": {"url": "mailto:john@doe.com", "body": ["john@doe.com"]}}],
            ),
            ("&amp; &copy; &#35;", ["& © #"]),
            ("line\nbreak", ["line break"]),
            ("hard  \nbreak", ["hard", {"linebreak": True}, "break"]),
            ("hard\\\nbreak", ["hard", {"linebreak": True}, "break"]),
            ("one\n\ntwo", ["one", {"parbreak": True}, "two"]),
            ("  surrounding spaces  ", ["surrounding spaces"]),
            ("", []),
        ],
    )
    def test_converts_markdown_to_rich_text(
        self, text: str, expected: RichText
    ) -> None:
        assert markdown_to_rich_text(text) == expected

    @pytest.mark.parametrize(
        "text",
        [
            "Raised $2M in funding",
            "$ single dollars $",
            "$$ unclosed math",
            "C# and F#",
            "#1 in the ranking",
            "@alice and @bob",
            "I <3 Typst",
            "x <y> z",
            "john@doe.com",
            "https://example.com",
            "a * b * c",
            "5 * 3 = 15",
            "snake_case_name",
            "back\\slash",
            "trailing backslash\\",
            "~~not strikethrough~~",
            "# not a heading",
            "- not a list",
            "1. not a list",
            "> not a quote",
            "| not | a | table |",
            "---",
            "{curly} (round) [square]",
            "\"quotes\" and 'apostrophes'",
            "=, +, /, %, ^, ~, |",
        ],
    )
    def test_keeps_hostile_text_literal(self, text: str) -> None:
        assert markdown_to_rich_text(text) == [text]

    def test_leaves_images_as_links(self) -> None:
        # Images aren't supported in CV text, so only the "!" stays behind:
        assert markdown_to_rich_text("![alt](photo.png)") == [
            "!",
            {"link": {"url": "photo.png", "body": ["alt"]}},
        ]

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("[text]()", ["text"]),
            ("before [text]() after", ["before text after"]),
            ("**[text]()**", [{"strong": ["text"]}]),
            ("[**text**]()", [{"strong": ["text"]}]),
        ],
    )
    def test_turns_links_without_url_into_text(
        self, text: str, expected: RichText
    ) -> None:
        assert markdown_to_rich_text(text) == expected

    @pytest.mark.parametrize(
        "text",
        ["**bold**", "***both***", "**[x]()**", "*a* **b**", "`a`**b**"],
    )
    def test_has_no_empty_strings(self, text: str) -> None:
        def strings(nodes: RichText) -> list[str]:
            found: list[str] = []
            for node in nodes:
                if isinstance(node, str):
                    found.append(node)
                elif "strong" in node or "emph" in node:
                    found.extend(strings(next(iter(node.values()))))
                elif "link" in node:
                    found.extend(strings(node["link"]["body"]))
            return found

        assert "" not in strings(markdown_to_rich_text(text))

    @pytest.mark.parametrize(
        "text",
        ["**not bold**", "$2M", "#emph[x]", "$$x$$", "# heading"],
    )
    def test_passes_typst_strings_as_typst(self, text: str) -> None:
        assert markdown_to_rich_text(TypstString(text)) == [{"typst": text}]

    @settings(deadline=None)
    @given(text=st.text())
    def test_never_raises(self, text: str) -> None:
        markdown_to_rich_text(text)

    @settings(deadline=None)
    @given(
        text=st.text(
            alphabet=st.characters(
                categories=["L", "N", "Zs"],
                include_characters="#%@^~|{}()+=:;,.?/'\"-!",
            ),
            min_size=1,
        ).filter(lambda text: text == text.strip() and text.strip() != "")
    )
    def test_keeps_plain_text_unchanged(self, text: str) -> None:
        nodes = markdown_to_rich_text(text)

        assert all(isinstance(node, str) for node in nodes)
        assert "".join(str(node) for node in nodes) == text


def test_get_markdown_parser() -> None:
    parser = get_markdown_parser()

    assert parser is get_markdown_parser()
    # Only inline syntax: block syntax would clash with the CV's structure.
    assert [token.type for token in parser.parse("# Title")] == [
        "paragraph_open",
        "inline",
        "paragraph_close",
    ]


class TestInlineTokensToRichText:
    def test_keeps_content_of_unknown_tokens(self) -> None:
        token = Token("html_inline", "", 0, content="<b>")

        assert inline_tokens_to_rich_text([token]) == ["<b>"]

    def test_skips_unknown_tokens_without_content(self) -> None:
        token = Token("image", "img", 0)

        assert inline_tokens_to_rich_text([token]) == []


@pytest.mark.parametrize(
    ("nodes", "expected"),
    [
        ([], []),
        (["a"], ["a"]),
        ([{"link": {"url": "", "body": ["a", "b"]}}], ["a", "b"]),
        (
            [{"strong": [{"link": {"url": "", "body": ["a"]}}]}],
            [{"strong": ["a"]}],
        ),
        (
            [{"emph": [{"link": {"url": "", "body": ["a"]}}]}],
            [{"emph": ["a"]}],
        ),
        (
            [
                {
                    "link": {
                        "url": "https://x.com",
                        "body": [{"link": {"url": "", "body": ["a"]}}],
                    }
                }
            ],
            [{"link": {"url": "https://x.com", "body": ["a"]}}],
        ),
        ([{"code": "x"}, {"math": "y"}], [{"code": "x"}, {"math": "y"}]),
    ],
)
def test_unwrap_empty_links(nodes: RichText, expected: RichText) -> None:
    assert unwrap_empty_links(nodes) == expected


@pytest.mark.parametrize(
    ("nodes", "expected"),
    [
        ([], []),
        (["a", "b", "c"], ["abc"]),
        (["a", {"code": "x"}, "b", "c"], ["a", {"code": "x"}, "bc"]),
        ([{"code": "x"}, {"code": "y"}], [{"code": "x"}, {"code": "y"}]),
    ],
)
def test_merge_text(nodes: RichText, expected: RichText) -> None:
    assert merge_text(nodes) == expected


class TestRichTextToPlainText:
    @pytest.mark.parametrize(
        ("markdown", "expected"),
        [
            ("Jane Doe", "Jane Doe"),
            ("Jane **Doe**", "Jane Doe"),
            ("*Jane* [Doe](https://example.com)", "Jane Doe"),
            ("`code` and $$x^2$$", "code and x^2"),
            ("Line  \nbreak", "Line break"),
            ("First\n\nSecond", "First Second"),
        ],
    )
    def test_drops_formatting(self, markdown: str, expected: str) -> None:
        assert rich_text_to_plain_text(markdown_to_rich_text(markdown)) == expected

    def test_keeps_typst_source(self) -> None:
        nodes = markdown_to_rich_text(TypstString("#strong[Jane]"))

        assert rich_text_to_plain_text(nodes) == "#strong[Jane]"
