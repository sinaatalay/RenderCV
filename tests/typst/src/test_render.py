import copy
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError

type TypstValue = Callable[..., Any]
type RenderedWords = Callable[..., list[tuple[str, str]]]
type CvData = Callable[..., dict[str, Any]]

prelude = """#import "/src/render.typ": render, render-entry, base-design, maximum-hand-overs
#import "/src/markdown.typ": to-markdown-document
#import "/src/entry-type.typ": entry-type, field, as-entry"""

cv: dict[str, Any] = {
    "name": "Jane Doe",
    "headline": "Engineer",
    "location": "Istanbul",
    "email": "jane@doe.com",
    "sections": {
        "summary": ["I build **things**."],
        "experience": {
            "Industry": [
                {
                    "company": "Acme",
                    "position": "Engineer",
                    "start_date": "2020-01",
                    "end_date": "present",
                    "highlights": ["Built it - with care"],
                }
            ],
        },
    },
}


def find_elements(node: Any, func: str) -> list[dict[str, Any]]:
    """Find every element of a kind in content, as a query returns it in JSON."""
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("func") == func:
            found.append(node)
        for value in node.values():
            found.extend(find_elements(value, func))
    elif isinstance(node, list):
        for item in node:
            found.extend(find_elements(item, func))
    return found


def render_markdown(
    typst_value: TypstValue,
    data: dict[str, Any],
    *,
    design: str = "base-design",
    types: str = "all-types",
    definitions: str = "",
) -> str:
    return typst_value(
        f"to-markdown-document(render(data, types: {types}, design: {design}))",
        prelude=prelude + "\n" + definitions,
        data=data,
    )


def test_base_design(typst_value: TypstValue) -> None:
    value = typst_value(
        "base-design.pairs().map(((key, value)) => (key, if type(value) =="
        ' function { "function" } else { value })).to-dict()',
        prelude=prelude,
    )

    assert value == {
        "name": "base",
        "options": {},
        "document": "function",
        "layout": "function",
        "header": "function",
        "section": "function",
        "entries": {},
    }


def test_maximum_hand_overs(typst_value: TypstValue) -> None:
    assert typst_value("maximum-hand-overs", prelude=prelude) == 16


class TestRender:
    def test_draws_a_semantic_document(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        assert render_markdown(typst_value, cv_data(cv)) == (
            "# Jane Doe\n\n"
            "Engineer\n\n"
            "Istanbul | [jane@doe.com](mailto:jane@doe.com)\n\n"
            "## Summary\n\n"
            "I build **things**.\n\n"
            "## Experience\n\n"
            "### Industry\n\n"
            "#### Acme, Engineer\n\n"
            "Jan 2020 – present\n\n"
            "- Built it\n\n"
            "  - with care\n"
        )

    def test_leaves_out_missing_header_parts(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data({"sections": {"summary": ["Text"]}})

        assert render_markdown(typst_value, data) == "## Summary\n\nText\n"

    def test_passes_document_information(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data(
            {"name": "Jane **Doe**"},
            settings={"pdf_title": "NAME's CV"},
            locale={"language": "german"},
        )

        info = typst_value(
            "render(data, design: (document: (body, info) => info))",
            prelude=prelude,
            data=data,
        )

        assert info["title"] == "Jane Doe's CV"
        assert info["author"] == ["Jane Doe"]
        assert info["keywords"] == []
        assert info["name"] == "Jane Doe"
        assert info["locale"]["language"] == "german"
        assert info["current-date"] == {
            "year": 2025,
            "month": 6,
            "day": 1,
            "present": False,
            "text": None,
        }
        assert info["settings"] == data["settings"]

    def test_has_no_author_without_a_name(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        info = typst_value(
            "render(data, design: (document: (body, info) => info))",
            prelude=prelude,
            data=cv_data({}),
        )

        assert info["author"] == []
        assert info["name"] is None

    def test_uses_the_base_design_for_what_a_design_leaves_out(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        markdown = render_markdown(
            typst_value,
            cv_data(cv),
            design="(header: (header, ctx) => [Header of #header.plain-name])",
        )

        assert markdown.startswith("Header of Jane Doe\n\n## Summary\n\n")

    def test_lets_designs_restyle_entry_types(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        markdown = render_markdown(
            typst_value,
            cv_data(cv),
            design=(
                "(entries: (experience: (it, ctx) => [#it.position at #it.company],"
                " paragraph: (it, ctx) => [Paragraph: #it.text]))"
            ),
        )

        assert "Paragraph: I build **things**." in markdown
        assert "Engineer at Acme" in markdown

    def test_draws_hand_overs_with_the_design_look_of_the_target(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        markdown = render_markdown(
            typst_value,
            cv_data(cv),
            design="(entries: (normal: (it, ctx) => [Normal: #it.name]))",
        )

        assert "Normal: Acme, Engineer" in markdown

    def test_passes_where_an_entry_is(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "skills": [
                        {"label": "A", "details": "1"},
                        {"label": "B", "details": "2"},
                    ],
                    "experience": {
                        "Industry": [{"company": "Acme", "position": "Engineer"}]
                    },
                }
            }
        )

        content = typst_value(
            "render(data, types: all-types, design: (entries: (one_line: (it, ctx) =>"
            " metadata((ctx.type, ctx.index, ctx.count, ctx.section.key,"
            " ctx.section.level, ctx.section.parent, ctx.locale.language,"
            " ctx.current-date.year)), normal: (it, ctx) => metadata((ctx.type,"
            " ctx.index, ctx.count, ctx.section.key, ctx.section.level,"
            " ctx.section.parent.key, ctx.locale.language,"
            " ctx.current-date.year)))))",
            prelude=prelude,
            data=data,
        )

        assert [element["value"] for element in find_elements(content, "metadata")] == [
            ["one_line", 1, 2, "skills", 1, None, "english", 2025],
            ["one_line", 2, 2, "skills", 1, None, "english", 2025],
            ["normal", 1, 1, "industry", 2, "experience", "english", 2025],
        ]

    def test_draws_nested_entries(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data({"name": "Jane Doe"})
        data["sections"] = [
            {
                "key": "projects",
                "title": ["Projects"],
                "entries": [
                    {
                        "type": "group",
                        "fields": {
                            "title": ["Group"],
                            "members": [
                                {"type": "paragraph", "fields": {"text": ["First"]}},
                                {"type": "paragraph", "fields": {"text": ["Second"]}},
                            ],
                        },
                    }
                ],
            }
        ]

        markdown = render_markdown(
            typst_value,
            data,
            types="all-types + (group: group)",
            definitions=(
                '#let group = entry-type(fields: (title: field("markdown"),'
                ' members: field("entries")), look: (it, ctx) => [#strong(it.title)'
                " #(ctx.render-entries)(it.members)])"
            ),
        )

        assert markdown == (
            "# Jane Doe\n\n## Projects\n\n**Group**\n\nFirst\n\nSecond\n"
        )

    @pytest.mark.parametrize(
        ("keywords", "bold_words"),
        [
            (["Python"], ["Python"]),
            (["Python", "C++", "AI"], ["Python", "C++", "AI"]),
            (["python"], []),
            (["Pyth"], []),
            (["C#", "a.b"], ["C#"]),
            (["", "AI"], ["AI"]),
            (["Machine Learning", "Machine"], ["Machine", "Learning", "Machine"]),
        ],
    )
    def test_bolds_keywords_as_whole_words(
        self,
        rendered_words: RenderedWords,
        cv_data: CvData,
        keywords: list[str],
        bold_words: list[str],
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "summary": [
                        "Python, Pythonic, C++ and C#, AI and AIR, axb,"
                        " Machine Learning and Machine."
                    ]
                }
            },
        )
        data = copy.deepcopy(data)
        data["settings"]["bold_keywords"] = keywords

        words = rendered_words(
            data, design="rendercv.base-design + (section: (s, body, ctx) => body)"
        )

        assert [word for word, weight in words if weight == "bold"] == bold_words


class TestRenderEntry:
    def test_draws_with_the_entry_type_look(self, typst_value: TypstValue) -> None:
        assert (
            typst_value(
                'render-entry((type: "one_line", fields: (label: ("A",), details:'
                ' ("B",))), all-types, base-design, (:))',
                prelude=prelude,
            )["func"]
            == "par"
        )

    def test_panics_on_hand_overs_to_unknown_types(
        self, typst_value: TypstValue
    ) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"An entry was handed over to the unknown entry type `talk`\.",
        ):
            typst_value(
                'render-entry((type: "paragraph", fields: (text: ("A",))),'
                " all-types, (entries: (paragraph: (it, ctx) =>"
                ' as-entry("talk"))), (:))',
                prelude=prelude,
            )

    def test_panics_on_hand_over_loops(self, typst_value: TypstValue) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"An entry of type `ping` is handed over in a loop\.",
        ):
            typst_value(
                'render-entry((type: "ping", fields: (:)), (ping: ping, pong: pong),'
                " (entries: (:)), (:))",
                prelude=prelude
                + '\n#let ping = entry-type(look: (it, ctx) => as-entry("pong"))'
                + '\n#let pong = entry-type(look: (it, ctx) => as-entry("ping"))',
            )

    def test_follows_chains_of_hand_overs(self, typst_value: TypstValue) -> None:
        value = typst_value(
            'render-entry((type: "a", fields: (x: "1")), (a: a, b: b, c: c), (entries:'
            " (:)), (:))",
            prelude=prelude
            + '\n#let a = entry-type(fields: (x: field("text")), look: (it, ctx) =>'
            ' as-entry("b", y: it.x + "2"))'
            + '\n#let b = entry-type(fields: (y: field("text"), unset:'
            ' field("text")), look: (it, ctx) => as-entry("c", z: it.y + "3",'
            " unset: it.unset))"
            + '\n#let c = entry-type(fields: (z: field("text"), unset:'
            ' field("text")), look: (it, ctx) => (it.z, it.unset, ctx.type))',
        )

        assert value == ["123", None, "c"]
