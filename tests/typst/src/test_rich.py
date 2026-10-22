from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError

type TypstValue = Callable[..., Any]
type TypstText = Callable[..., str]

prelude = '#import "/src/rich.typ": rich, rich-nodes'


class TestRich:
    @pytest.mark.parametrize("value", [None, []])
    def test_returns_none_for_nothing(
        self, typst_value: TypstValue, value: Any
    ) -> None:
        assert (
            typst_value("rich(data.value)", prelude=prelude, data={"value": value})
            is None
        )

    def test_shows_strings_literally(self, typst_value: TypstValue) -> None:
        text = "#strong[x] $2M *not bold* @alice <3 \\ ` = heading"

        assert typst_value(
            "rich(data.value)", prelude=prelude, data={"value": text}
        ) == {"func": "text", "text": text}

    def test_returns_content_as_is(self, typst_value: TypstValue) -> None:
        assert typst_value("rich([*bold*])", prelude=prelude) == {
            "func": "strong",
            "body": {"func": "text", "text": "bold"},
        }

    def test_draws_rich_text_nodes(self, typst_value: TypstValue) -> None:
        nodes = [
            "Raised ",
            {"strong": ["$18M"]},
            " for ",
            {"link": {"url": "https://x.com", "body": [{"emph": ["X"]}]}},
            {"linebreak": True},
            {"code": "a * b"},
            {"parbreak": True},
            "C# #1",
        ]

        assert typst_value(
            "rich(data.value)", prelude=prelude, data={"value": nodes}
        ) == {
            "func": "sequence",
            "children": [
                {"func": "text", "text": "Raised "},
                {"func": "strong", "body": {"func": "text", "text": "$18M"}},
                {"func": "text", "text": " for "},
                {
                    "func": "link",
                    "dest": "https://x.com",
                    "body": {"func": "emph", "body": {"func": "text", "text": "X"}},
                },
                {"func": "linebreak"},
                {"func": "raw", "text": "a * b"},
                {"func": "parbreak"},
                {"func": "text", "text": "C# #1"},
            ],
        }

    def test_draws_math_with_its_source_as_alternative_text(
        self, typst_value: TypstValue
    ) -> None:
        value = typst_value(
            "rich(data.value)", prelude=prelude, data={"value": [{"math": "x^2"}]}
        )

        assert value == {
            "func": "equation",
            "alt": "x^2",
            "body": {
                "func": "attach",
                "base": {"func": "symbol", "text": "x"},
                "t": {"func": "text", "text": "2"},
            },
        }

    def test_evaluates_typst_nodes(self, typst_value: TypstValue) -> None:
        value = typst_value(
            "rich(data.value)",
            prelude=prelude,
            data={"value": [{"typst": "#emph[x] *y*"}]},
        )

        assert value == {
            "func": "sequence",
            "children": [
                {"func": "emph", "body": {"func": "text", "text": "x"}},
                {"func": "space"},
                {"func": "strong", "body": {"func": "text", "text": "y"}},
            ],
        }

    @pytest.mark.parametrize("node", [{"unknown": 1}, {"strng": ["typo"]}])
    def test_panics_on_unknown_nodes(
        self, typst_value: TypstValue, node: dict[str, Any]
    ) -> None:
        with pytest.raises(RenderCVUserError, match="Unknown rich text node"):
            typst_value("rich(data.value)", prelude=prelude, data={"value": [node]})


def test_rich_nodes(typst_text: TypstText) -> None:
    text = typst_text(
        "rich-nodes(data.value)",
        prelude=prelude,
        data={"value": ["a", {"strong": ["b", {"emph": ["c"]}]}, "d"]},
    )

    assert text == "abcd"
