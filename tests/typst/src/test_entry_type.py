from collections.abc import Callable
from typing import Any

import pytest

type TypstValue = Callable[..., Any]

prelude = '#import "/src/entry-type.typ": *'

talk = (
    'entry-type(doc: "A talk.", fields: (title: field("markdown", doc: "The'
    ' title."), when: field("date", optional: true, allow-text: true)), look:'
    ' (it, ctx) => as-entry("normal", name: it.title))'
)


class TestField:
    def test_has_defaults(self, typst_value: TypstValue) -> None:
        assert typst_value('field("markdown")', prelude=prelude) == {
            "rendercv-field": True,
            "kind": "markdown",
            "optional": False,
            "doc": None,
            "of": None,
            "choices": None,
            "pattern": None,
            "allow-text": False,
        }

    def test_keeps_every_setting(self, typst_value: TypstValue) -> None:
        value = typst_value(
            'field("choice", optional: true, doc: "Level.", of: "text", choices:'
            ' ("a", "b"), pattern: "[ab]", allow-text: true)',
            prelude=prelude,
        )

        assert value == {
            "rendercv-field": True,
            "kind": "choice",
            "optional": True,
            "doc": "Level.",
            "of": "text",
            "choices": ["a", "b"],
            "pattern": "[ab]",
            "allow-text": True,
        }


def test_entry_type(typst_value: TypstValue) -> None:
    value = typst_value(
        f"{talk}.pairs().map(((key, value)) => (key, if type(value) == function"
        ' { "function" } else { value })).to-dict()',
        prelude=prelude,
    )

    assert value == {
        "rendercv-entry-type": True,
        "fields": {
            "title": {
                "rendercv-field": True,
                "kind": "markdown",
                "optional": False,
                "doc": "The title.",
                "of": None,
                "choices": None,
                "pattern": None,
                "allow-text": False,
            },
            "when": {
                "rendercv-field": True,
                "kind": "date",
                "optional": True,
                "doc": None,
                "of": None,
                "choices": None,
                "pattern": None,
                "allow-text": True,
            },
        },
        "look": "function",
        "doc": "A talk.",
    }


def test_as_entry(typst_value: TypstValue) -> None:
    assert typst_value(
        'as-entry("normal", name: [X], date: none)', prelude=prelude
    ) == {
        "rendercv-as": "normal",
        "fields": {"name": {"func": "text", "text": "X"}, "date": None},
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (talk, True),
        ("(rendercv-entry-type: true)", True),
        ("(rendercv-entry-type: false)", False),
        ("(fields: (:), look: none)", False),
        ('field("text")', False),
        ('as-entry("normal")', False),
        ("42", False),
    ],
)
def test_is_entry_type(typst_value: TypstValue, value: str, expected: bool) -> None:
    assert typst_value(f"is-entry-type({value})", prelude=prelude) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ('as-entry("normal", name: [X])', True),
        ("(rendercv-as: none)", False),
        (talk, False),
        ("[content]", False),
        ("none", False),
    ],
)
def test_is_hand_over(typst_value: TypstValue, value: str, expected: bool) -> None:
    assert typst_value(f"is-hand-over({value})", prelude=prelude) is expected


def test_collect_entry_types(typst_value: TypstValue) -> None:
    value = typst_value(
        f"collect-entry-types((talk: {talk}, number: 1, helper: x => x, field:"
        ' field("text"), types: (talk: 1))).keys()',
        prelude=prelude,
    )

    assert value == ["talk"]


def test_collect_entry_types_from_the_package(typst_value: TypstValue) -> None:
    value = typst_value("rendercv.collect-entry-types(dictionary(rendercv)).keys()")

    assert sorted(value) == sorted(
        [
            "normal",
            "experience",
            "education",
            "publication",
            "one_line",
            "bullet",
            "numbered",
            "reversed_numbered",
            "paragraph",
        ]
    )


def test_declarations(typst_value: TypstValue) -> None:
    value = typst_value(f"declarations((talk: {talk}))", prelude=prelude)

    assert value == {
        "talk": {
            "doc": "A talk.",
            "fields": {
                "title": {
                    "kind": "markdown",
                    "optional": False,
                    "doc": "The title.",
                    "of": None,
                    "choices": None,
                    "pattern": None,
                    "allow-text": False,
                },
                "when": {
                    "kind": "date",
                    "optional": True,
                    "doc": None,
                    "of": None,
                    "choices": None,
                    "pattern": None,
                    "allow-text": True,
                },
            },
        }
    }
