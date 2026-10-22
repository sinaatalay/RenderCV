from collections.abc import Callable
from typing import Any

import pytest

type TypstValue = Callable[..., Any]

prelude = '#import "/src/markdown.typ": *'


def to_markdown(typst_value: TypstValue, content: str, *, plain: bool) -> str:
    return typst_value(
        f"to-markdown({content}, plain: {'true' if plain else 'false'})",
        prelude=prelude,
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("plain text", "plain text"),
        ("a*b_c", "a\\*b\\_c"),
        ("[link](url)", "\\[link\\](url)"),
        ("back\\slash `code`", "back\\\\slash \\`code\\`"),
        ("# $2M @alice <3", "# $2M @alice <3"),
    ],
)
def test_escape_markdown(typst_value: TypstValue, text: str, expected: str) -> None:
    assert (
        typst_value("escape-markdown(data.text)", prelude=prelude, data={"text": text})
        == expected
    )


class TestToMarkdown:
    @pytest.mark.parametrize(
        ("content", "markdown", "plain"),
        [
            ("none", "", ""),
            ("42", "42", "42"),
            ('"a*b"', "a\\*b", "a*b"),
            ("[a*b]", "a\\*b", "a*b"),
            ("[a b]", "a b", "a b"),
            ("[a\n\nb]", "a\n\nb", "a\n\nb"),
            ("[\"x\" 'y']", "\"x\" 'y'", "\"x\" 'y'"),
            ("[*x*]", "**x**", "x"),
            ("[_x_]", "*x*", "x"),
            ("strong[a #emph[b]]", "**a *b***", "a b"),
            ("[`a*b`]", "`a*b`", "a*b"),
            ('link("https://x.com")[X]', "[X](https://x.com)", "X"),
            ("link(<somewhere>)[X]", "X", "X"),
            ("par[P]", "\n\nP\n\n", "\n\nP\n\n"),
            ("heading(level: 3)[T]", "\n\n### T\n\n", "\n\nT\n\n"),
            ("heading[T]", "\n\n# T\n\n", "\n\nT\n\n"),
            ("[== T]", "\n\n## T\n\n", "\n\nT\n\n"),
            ('math.equation(alt: "x^2", $x^2$.body)', "$$x^2$$", "x^2"),
            ("[a#h(1cm)b]", "a b", "a b"),
            ("text(fill: red)[x]", "x", "x"),
            ("box[x]", "x", "x"),
            ("align(center)[x]", "x", "x"),
            ("sym.arrow", "→", "→"),
            ("line()", "", ""),
            ("[]", "", ""),
            ("strong[]", "****", ""),
        ],
    )
    def test_converts_inline_content(
        self, typst_value: TypstValue, content: str, markdown: str, plain: str
    ) -> None:
        assert to_markdown(typst_value, content, plain=False) == markdown
        assert to_markdown(typst_value, content, plain=True) == plain

    @pytest.mark.parametrize(
        ("content", "markdown", "plain"),
        [
            ("[a \\ b]", "a   \n b", "a \n b"),
            ("[a#linebreak()b]", "a  \nb", "a\nb"),
        ],
    )
    def test_converts_line_breaks(
        self, typst_value: TypstValue, content: str, markdown: str, plain: str
    ) -> None:
        assert to_markdown(typst_value, content, plain=False) == markdown
        assert to_markdown(typst_value, content, plain=True) == plain

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ("list[a][b]", "\n\n- a\n- b\n\n"),
            ("enum[a][b]", "\n\n1. a\n2. b\n\n"),
            ("enum(enum.item(5)[x], [y])", "\n\n5. x\n2. y\n\n"),
            # Nested lists are separated by a blank line, which makes the outer
            # list a loose one in Markdown:
            ("list([a #list[b][c]], [d])", "\n\n- a \n\n  - b\n  - c\n- d\n\n"),
            ("list()", "\n\n\n\n"),
            ("[- a\n- b]", "\n- a \n- b"),
            ("[+ a\n+ b]", "\n1. a \n1. b"),
        ],
    )
    def test_converts_lists(
        self, typst_value: TypstValue, content: str, expected: str
    ) -> None:
        assert to_markdown(typst_value, content, plain=False) == expected

    @pytest.mark.parametrize(
        "content",
        [
            "[#metadata(1)x]",
            "[#place[hidden]x]",
            "[#v(1cm)x]",
            "[#image(bytes(\"<svg xmlns='http://www.w3.org/2000/svg'/>\"))x]",
            "[#pagebreak()x]",
            "[#counter(page).update(1)x]",
            '[#state("s").update(1)x]',
            "[#context [hidden]x]",
        ],
    )
    def test_skips_invisible_and_layout_content(
        self, typst_value: TypstValue, content: str
    ) -> None:
        assert to_markdown(typst_value, content, plain=False) == "x"

    @pytest.mark.parametrize(
        "content",
        [
            "grid(columns: 2, [a], [b], [], [c])",
            "table(columns: 2, [a], [b], [], [c])",
        ],
    )
    def test_puts_cells_in_paragraphs(
        self, typst_value: TypstValue, content: str
    ) -> None:
        assert to_markdown(typst_value, content, plain=False) == "a\n\nb\n\nc"

    def test_skips_empty_grids(self, typst_value: TypstValue) -> None:
        assert to_markdown(typst_value, "grid([], [])", plain=False) == ""


class TestToMarkdownDocument:
    def test_tidies_blank_lines_and_trailing_spaces(
        self, typst_value: TypstValue
    ) -> None:
        text = "\n\n\n\nA \n\n\n\nB   \nC\t\n"

        assert (
            typst_value(
                "to-markdown-document(data.text)",
                prelude=prelude,
                data={"text": text},
            )
            == "A\n\nB  \nC\n"
        )
        assert (
            typst_value(
                "to-markdown-document(data.text, plain: true)",
                prelude=prelude,
                data={"text": text},
            )
            == "A\n\nB\nC\n"
        )

    def test_converts_a_document(self, typst_value: TypstValue) -> None:
        document = (
            "[= Jane Doe\n\n"
            'Engineer at #link("https://x.com")[X]\n\n'
            "== Experience\n\n"
            "#heading(level: 3)[*Acme*, Engineer]\n\n"
            '#list[Built _things_][Shipped #raw("code")]\n\n'
            "Done.]"
        )

        assert typst_value(f"to-markdown-document({document})", prelude=prelude) == (
            "# Jane Doe\n\n"
            "Engineer at [X](https://x.com)\n\n"
            "## Experience\n\n"
            "### **Acme**, Engineer\n\n"
            "- Built *things*\n"
            "- Shipped `code`\n\n"
            "Done.\n"
        )

    def test_writes_markup_lists_as_tight_lists(self, typst_value: TypstValue) -> None:
        assert typst_value(
            "to-markdown-document([Intro\n- a\n- b\n\nOutro])", prelude=prelude
        ) == ("Intro\n- a\n- b\n\nOutro\n")
