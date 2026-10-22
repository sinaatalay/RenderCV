from collections.abc import Callable
from typing import Any

import pytest

type TypstValue = Callable[..., Any]
type TypstText = Callable[..., str]

prelude = '#import "/src/values.typ": field-value, entry-values, bullet-list'

bullets = [
    {
        "body": ["Published ", {"strong": ["papers"]}],
        "children": [{"body": ["ICML"], "children": []}],
    },
    {"body": ["Taught"]},
]


class TestFieldValue:
    @pytest.mark.parametrize(
        ("value", "kind", "expected"),
        [
            (None, "markdown", None),
            ("plain", "text", "plain"),
            ("https://x.com", "url", "https://x.com"),
            ("a@b.com", "email", "a@b.com"),
            ("b", "choice", "b"),
            (3, "number", 3),
            (True, "bool", True),
            (
                {"e164": "+1", "international": "+1", "national": "1", "uri": "tel:+1"},
                "phone",
                {"e164": "+1", "international": "+1", "national": "1", "uri": "tel:+1"},
            ),
            (
                {"year": 2020},
                "date",
                {
                    "year": 2020,
                    "month": None,
                    "day": None,
                    "present": False,
                    "text": None,
                },
            ),
        ],
    )
    def test_passes_simple_values(
        self, typst_value: TypstValue, value: Any, kind: str, expected: Any
    ) -> None:
        assert (
            typst_value(
                f'field-value(data.value, (kind: "{kind}"))',
                prelude=prelude,
                data={"value": value},
            )
            == expected
        )

    def test_turns_markdown_into_content(self, typst_value: TypstValue) -> None:
        assert typst_value(
            'field-value(data.value, (kind: "markdown"))',
            prelude=prelude,
            data={"value": [{"emph": ["x"]}]},
        ) == {"func": "emph", "body": {"func": "text", "text": "x"}}

    def test_turns_bullets_into_content_with_children(
        self, typst_value: TypstValue
    ) -> None:
        value = typst_value(
            'field-value(data.value, (kind: "bullets"))',
            prelude=prelude,
            data={"value": bullets},
        )

        assert value == [
            {
                "body": {
                    "func": "sequence",
                    "children": [
                        {"func": "text", "text": "Published "},
                        {"func": "strong", "body": {"func": "text", "text": "papers"}},
                    ],
                },
                "children": [
                    {"body": {"func": "text", "text": "ICML"}, "children": []}
                ],
            },
            {"body": {"func": "text", "text": "Taught"}, "children": []},
        ]

    @pytest.mark.parametrize(
        ("of", "value", "expected"),
        [
            ("text", ["a", "b"], ["a", "b"]),
            (
                "markdown",
                [["a"], [{"strong": ["b"]}]],
                [
                    {"func": "text", "text": "a"},
                    {"func": "strong", "body": {"func": "text", "text": "b"}},
                ],
            ),
            (
                "date",
                [{"present": True}],
                [
                    {
                        "year": None,
                        "month": None,
                        "day": None,
                        "present": True,
                        "text": None,
                    }
                ],
            ),
        ],
    )
    def test_converts_each_item_of_lists(
        self, typst_value: TypstValue, of: str, value: list[Any], expected: list[Any]
    ) -> None:
        assert (
            typst_value(
                f'field-value(data.value, (kind: "list", of: "{of}"))',
                prelude=prelude,
                data={"value": value},
            )
            == expected
        )


class TestEntryValues:
    def test_fills_in_every_declared_field(self, typst_value: TypstValue) -> None:
        value = typst_value(
            'entry-values(data.values, (name: (kind: "markdown"), date: (kind:'
            ' "date"), tags: (kind: "list", of: "text")))',
            prelude=prelude,
            data={"values": {"name": ["X"]}},
        )

        assert value == {
            "name": {"func": "text", "text": "X"},
            "date": None,
            "tags": None,
        }

    def test_leaves_out_undeclared_fields(self, typst_value: TypstValue) -> None:
        value = typst_value(
            'entry-values(data.values, (name: (kind: "text"),))',
            prelude=prelude,
            data={"values": {"name": "X", "extra": "Y"}},
        )

        assert value == {"name": "X"}


class TestBulletList:
    @pytest.mark.parametrize("value", [None, []])
    def test_draws_nothing_without_bullets(
        self, typst_value: TypstValue, value: Any
    ) -> None:
        assert (
            typst_value(
                "bullet-list(data.value)", prelude=prelude, data={"value": value}
            )
            is None
        )

    def test_nests_bullets(self, typst_value: TypstValue) -> None:
        value = typst_value(
            'bullet-list(field-value(data.value, (kind: "bullets")))',
            prelude=prelude,
            data={"value": bullets},
        )

        assert value["func"] == "list"
        first, second = value["children"]
        assert first["body"]["children"][-1] == {
            "func": "list",
            "children": [{"func": "item", "body": {"func": "text", "text": "ICML"}}],
        }
        assert second == {"func": "item", "body": {"func": "text", "text": "Taught"}}
