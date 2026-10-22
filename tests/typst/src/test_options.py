from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError

type TypstValue = Callable[..., Any]

prelude = (
    '#import "/src/options.typ": merge-options, is-compatible, edit-distance,'
    " closest-option"
)

defaults = (
    '(page: (size: "a4", margin: 1cm), colors: (name: blue, body: black),'
    ' spacing: 1.2em, count: 3, label: "x", fill: none, width: auto)'
)


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        ("1cm", "2cm", True),
        ("50%", "2cm", True),
        ("1em + 2pt", "2cm", True),
        ("1fr", "2cm", True),
        ("2", "1.5", True),
        ("1.5", "2", True),
        ("gradient.linear(red, blue)", "red", True),
        ("[content]", '"string"', True),
        ("sym.bullet", '"string"', True),
        ('"anything"', "none", True),
        ('"anything"', "auto", True),
        ("none", "1cm", True),
        ("auto", "1cm", True),
        ("(a: 1)", "(b: 2)", True),
        ('"1cm"', "1cm", False),
        ("1cm", '"1cm"', False),
        ("true", "1", False),
        ("red", "1cm", False),
        ("(1, 2)", '"x"', False),
    ],
)
def test_is_compatible(
    typst_value: TypstValue, value: str, default: str, expected: bool
) -> None:
    assert typst_value(f"is-compatible({value}, {default})", prelude=prelude) is (
        expected
    )


class TestMergeOptions:
    def test_returns_the_defaults_without_values(self, typst_value: TypstValue) -> None:
        assert typst_value(
            f"merge-options({defaults}, (:)) == {defaults}", prelude=prelude
        )

    def test_merges_nested_values_key_by_key(self, typst_value: TypstValue) -> None:
        assert typst_value(
            f'merge-options({defaults}, (page: (size: "us-letter"), colors: (name:'
            " red), spacing: 50%, count: 2.5, label: [x], fill: red, width: 5cm))"
            ' == (page: (size: "us-letter", margin: 1cm), colors: (name: red,'
            " body: black), spacing: 50%, count: 2.5, label: [x], fill: red, width:"
            " 5cm)",
            prelude=prelude,
        )

    def test_replaces_a_dictionary_by_a_non_dictionary(
        self, typst_value: TypstValue
    ) -> None:
        # Values of other types than the default are errors, but `none` is
        # always allowed:
        assert (
            typst_value(
                f"merge-options({defaults}, (colors: none)).colors", prelude=prelude
            )
            is None
        )

    @pytest.mark.parametrize(
        ("values", "message"),
        [
            (
                "(colours: (name: red))",
                "Unknown design option `colours`. Did you mean `colors`? Available"
                " options here: `page`, `colors`, `spacing`, `count`, `label`,"
                " `fill`, `width`.",
            ),
            (
                '(page: (sise: "a4"))',
                "Unknown design option `page.sise`. Did you mean `size`? Available"
                " options here: `size`, `margin`.",
            ),
            (
                "(colors: (name: (dark: red)))",
                "Design option `colors.name` should be of type color, but got"
                ' (dark: rgb("#ff4136")).',
            ),
            (
                '(page: (margin: "1cm"))',
                'Design option `page.margin` should be of type length, but got "1cm".',
            ),
            (
                "(count: true)",
                "Design option `count` should be of type integer, but got true.",
            ),
        ],
    )
    def test_explains_unknown_options_and_wrong_types(
        self, typst_value: TypstValue, values: str, message: str
    ) -> None:
        with pytest.raises(RenderCVUserError) as error:
            typst_value(f"merge-options({defaults}, {values})", prelude=prelude)

        assert str(error.value.message).startswith(
            f"Typst couldn't compile the CV: {message}\n"
        )


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ("", "", 0),
        ("size", "size", 0),
        ("sise", "size", 1),
        ("", "abc", 3),
        ("kitten", "sitting", 3),
    ],
)
def test_edit_distance(typst_value: TypstValue, a: str, b: str, expected: int) -> None:
    assert typst_value(f'edit-distance("{a}", "{b}")', prelude=prelude) == expected


@pytest.mark.parametrize(
    ("key", "expected"),
    [("colours", "colors"), ("sise", "size"), ("zzzzzz", None), ("x", None)],
)
def test_closest_option(
    typst_value: TypstValue, key: str, expected: str | None
) -> None:
    options = '("size", "colors", "margin")'

    assert (
        typst_value(f'closest-option("{key}", {options})', prelude=prelude) == expected
    )
