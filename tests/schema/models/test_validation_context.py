import pathlib
from collections.abc import Callable
from datetime import date as Date
from typing import Any

import pydantic
import pytest

from rendercv.schema.models.validation_context import (
    ValidationContext,
    get_current_date,
    get_input_file_path,
    get_validation_context,
)


def read_context[T](
    function: Callable[[pydantic.ValidationInfo], T], context: dict[str, Any] | None
) -> T:
    """Return what `function` returns for the context during validation."""
    results: list[T] = []

    class Reader(pydantic.BaseModel):
        value: Any

        @pydantic.field_validator("value")
        @classmethod
        def read(cls, value: Any, info: pydantic.ValidationInfo) -> Any:
            results.append(function(info))
            return value

    Reader.model_validate({"value": None}, context=context)
    return results[0]


def test_validation_context() -> None:
    context = ValidationContext()

    assert context.input_file_path is None
    assert context.current_date is None
    assert context.entry_types == {}
    assert context.entry_type_models == {}


class TestGetValidationContext:
    def test_returns_the_given_context(self) -> None:
        context = ValidationContext(input_file_path=pathlib.Path("cv.yaml"))

        assert read_context(get_validation_context, {"context": context}) is context

    @pytest.mark.parametrize("context", [None, {}, {"other": 1}])
    def test_returns_an_empty_context_without_one(
        self, context: dict[str, Any] | None
    ) -> None:
        assert read_context(get_validation_context, context) == ValidationContext()


class TestGetInputFilePath:
    def test_returns_the_input_file_path(self) -> None:
        path = pathlib.Path("/test/input/file.yaml")

        result = read_context(
            get_input_file_path, {"context": ValidationContext(input_file_path=path)}
        )

        assert result == path

    @pytest.mark.parametrize("context", [None, {"context": ValidationContext()}])
    def test_returns_none_without_an_input_file(
        self, context: dict[str, Any] | None
    ) -> None:
        assert read_context(get_input_file_path, context) is None


class TestGetCurrentDate:
    def test_returns_the_given_date(self) -> None:
        date = Date(2008, 1, 15)

        result = read_context(
            get_current_date, {"context": ValidationContext(current_date=date)}
        )

        assert result == date

    @pytest.mark.parametrize(
        "context",
        [
            None,
            {"context": ValidationContext(current_date="today")},
            {"context": ValidationContext(current_date="not a date")},
        ],
    )
    def test_defaults_to_today(self, context: dict[str, Any] | None) -> None:
        assert read_context(get_current_date, context) == Date.today()
