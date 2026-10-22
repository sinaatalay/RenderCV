from collections.abc import Callable
from typing import Any

import pytest

type TypstValue = Callable[..., Any]
type TypstText = Callable[..., str]
type CvData = Callable[..., dict[str, Any]]

prelude = '#import "/entries/standard.typ": *'

when_fields = ["date", "start_date", "end_date"]
detail_fields = ["location", "summary", "highlights"]

# The standard entry types keep RenderCV 2's field names, so v2 CVs still work.
standard_fields: dict[str, tuple[list[str], list[str]]] = {
    "normal": (["name", *when_fields, *detail_fields], ["name"]),
    "experience": (
        ["company", "position", *when_fields, *detail_fields],
        ["company", "position"],
    ),
    "education": (
        ["institution", "area", "degree", *when_fields, *detail_fields],
        ["institution", "area"],
    ),
    "publication": (
        ["title", "authors", "summary", "doi", "url", "journal", "date"],
        ["title", "authors"],
    ),
    "one_line": (["label", "details"], ["label", "details"]),
    "bullet": (["bullet"], ["bullet"]),
    "numbered": (["number"], ["number"]),
    "reversed_numbered": (["reversed_number"], ["reversed_number"]),
    "paragraph": (["text"], ["text"]),
}


def render_markdown(
    typst_value: TypstValue, data: dict[str, Any], design: str = "base-design"
) -> str:
    return typst_value(
        "rendercv.to-markdown-document(rendercv.render(data, types: all-types,"
        f" design: rendercv.{design}))",
        data=data,
    )


class TestDeclarations:
    @pytest.mark.parametrize(
        ("name", "fields", "required"),
        [(name, *fields) for name, fields in standard_fields.items()],
    )
    def test_keeps_the_field_names_of_rendercv_2(
        self,
        typst_value: TypstValue,
        name: str,
        fields: list[str],
        required: list[str],
    ) -> None:
        declaration = typst_value(
            f"rendercv.declarations((it: {name})).it", prelude=prelude
        )

        assert list(declaration["fields"]) == fields
        assert [
            field_name
            for field_name, field in declaration["fields"].items()
            if not field["optional"]
        ] == required
        assert declaration["doc"]
        assert all(field["doc"] for field in declaration["fields"].values())

    def test_declares_every_standard_type(self, typst_value: TypstValue) -> None:
        declarations = typst_value("rendercv.declarations(all-types)")

        assert sorted(declarations) == sorted(standard_fields)

    @pytest.mark.parametrize(
        ("name", "field", "expected"),
        [
            ("normal", "date", {"kind": "date", "allow-text": True}),
            ("normal", "start_date", {"kind": "date", "allow-text": False}),
            ("normal", "end_date", {"kind": "date", "allow-text": False}),
            ("normal", "highlights", {"kind": "bullets"}),
            ("normal", "summary", {"kind": "markdown"}),
            ("publication", "authors", {"kind": "list", "of": "markdown"}),
            ("publication", "doi", {"kind": "text", "pattern": "10\\..+"}),
            ("publication", "url", {"kind": "url"}),
            ("publication", "date", {"kind": "date", "allow-text": True}),
        ],
    )
    def test_uses_the_right_field_kinds(
        self,
        typst_value: TypstValue,
        name: str,
        field: str,
        expected: dict[str, Any],
    ) -> None:
        declaration = typst_value(
            f'rendercv.declarations((it: {name})).it.fields.at("{field}")',
            prelude=prelude,
        )

        assert {key: declaration[key] for key in expected} == expected


class TestLooks:
    @pytest.mark.parametrize(
        ("entry", "expected"),
        [
            (
                {
                    "name": "Project",
                    "date": "2021",
                    "location": "Remote",
                    "summary": "A *summary*",
                    "highlights": ["First - nested", "Second"],
                },
                "### Project\n\nRemote | 2021\n\nA *summary*\n\n"
                "- First\n\n  - nested\n- Second\n",
            ),
            (
                {
                    "company": "Acme",
                    "position": "Engineer",
                    "start_date": "2020-01",
                    "end_date": "2021-02",
                },
                "### Acme, Engineer\n\nJan 2020 – Feb 2021\n",
            ),
            (
                {"institution": "MIT", "area": "Physics", "degree": "PhD"},
                "### MIT, PhD in Physics\n",
            ),
            ({"institution": "MIT", "area": "Physics"}, "### MIT, Physics\n"),
            (
                {
                    "title": "A Paper",
                    "authors": ["**Jane Doe**", "Bob"],
                    "doi": "10.1234/x",
                    "journal": "Nature",
                    "date": "2020-05",
                },
                "### A Paper\n\nMay 2020\n\n**Jane Doe**, Bob  \n"
                "[10.1234/x](https://doi.org/10.1234/x) (Nature)\n",
            ),
            (
                {
                    "title": "A Paper",
                    "authors": ["Jane Doe"],
                    "url": "https://www.example.com/paper/",
                    "summary": "Summary",
                },
                "### A Paper\n\nSummary  \nJane Doe  \n"
                "[example.com/paper](https://www.example.com/paper/)\n",
            ),
            (
                {"title": "A Paper", "authors": ["Jane Doe"]},
                "### A Paper\n\nJane Doe\n",
            ),
            (
                {"label": "Languages", "details": "English, *Turkish*"},
                "**Languages:** English, *Turkish*\n",
            ),
            ({"bullet": "A point"}, "- A point\n"),
            ({"number": "First"}, "1. First\n"),
            ({"reversed_number": "Latest"}, "1. Latest\n"),
            ("Just **text**.", "Just **text**.\n"),
        ],
    )
    def test_draws_every_standard_type(
        self,
        typst_value: TypstValue,
        cv_data: CvData,
        entry: dict[str, Any] | str,
        expected: str,
    ) -> None:
        data = cv_data({"sections": {"section": [entry]}})

        assert render_markdown(typst_value, data) == "## Section\n\n" + expected

    def test_numbers_entries(self, typst_value: TypstValue, cv_data: CvData) -> None:
        data = cv_data(
            {
                "sections": {
                    "numbered": [{"number": "A"}, {"number": "B"}, {"number": "C"}],
                    "reversed": [
                        {"reversed_number": "A"},
                        {"reversed_number": "B"},
                        {"reversed_number": "C"},
                    ],
                }
            }
        )

        assert render_markdown(typst_value, data) == (
            "## Numbered\n\n1. A\n\n2. B\n\n3. C\n\n"
            "## Reversed\n\n3. A\n\n2. B\n\n1. C\n"
        )

    def test_hands_over_to_normal(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "section": [
                        {"company": "Acme", "position": "Engineer"},
                        {"institution": "MIT", "area": "Physics"},
                        {"title": "A Paper", "authors": ["Jane Doe"]},
                    ]
                }
            }
        )

        markdown = typst_value(
            "rendercv.to-markdown-document(rendercv.render(data, types: all-types,"
            " design: (entries: (normal: (it, ctx) => [Normal: #it.name\n\n]))))",
            data=data,
        )

        assert markdown == (
            "## Section\n\nNormal: Acme, Engineer\n\nNormal: MIT, Physics\n\n"
            "Normal: A Paper\n"
        )


class TestDegreeWithArea:
    @pytest.mark.parametrize(
        ("phrase", "expected"),
        [
            ("#degree in #area", "PhD in Physics"),
            ("#area, #degree", "Physics, PhD"),
            ("#degree (#area)", "PhD (Physics)"),
            ("*#degree* -- #area", "PhD – Physics"),
        ],
    )
    def test_uses_the_locale_phrase(
        self, typst_text: TypstText, phrase: str, expected: str
    ) -> None:
        text = typst_text(
            "degree-with-area((degree: [PhD], area: [Physics]), (locale: (phrases:"
            " (degree_with_area: data.phrase))))",
            prelude=prelude,
            data={"phrase": phrase},
        )

        assert text == expected

    def test_writes_only_the_area_without_a_degree(self, typst_text: TypstText) -> None:
        text = typst_text(
            "degree-with-area((degree: none, area: [Physics]), (locale: (phrases:"
            ' (degree_with_area: "#degree in #area"))))',
            prelude=prelude,
        )

        assert text == "Physics"

    def test_uses_the_turkish_word_order(
        self, typst_value: TypstValue, cv_data: CvData
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "education": [
                        {"institution": "ODTÜ", "area": "Fizik", "degree": "Lisans"}
                    ]
                }
            },
            locale={"language": "turkish"},
        )

        assert render_markdown(typst_value, data) == (
            "## Education\n\n### ODTÜ, Fizik, Lisans\n"
        )


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        (
            '(doi: "10.1/x", url: "https://x.com")',
            {"func": "link", "dest": "https://doi.org/10.1/x", "body": "10.1/x"},
        ),
        (
            '(doi: none, url: "https://www.x.com/a/")',
            {"func": "link", "dest": "https://www.x.com/a/", "body": "x.com/a"},
        ),
        ("(doi: none, url: none)", None),
    ],
)
def test_publication_link(
    typst_value: TypstValue, fields: str, expected: dict[str, Any] | None
) -> None:
    value = typst_value(f"publication-link({fields})", prelude=prelude)

    if expected is None:
        assert value is None
    else:
        assert value["func"] == expected["func"]
        assert value["dest"] == expected["dest"]
        assert value["body"]["text"] == expected["body"]
