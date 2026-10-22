import pathlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date as Date
from typing import TYPE_CHECKING, Any, cast

import pydantic

if TYPE_CHECKING:
    from .cv.entry_types import EntryTypeDeclaration


@dataclass
class ValidationContext:
    """What validators need to know beyond the YAML itself.

    Why:
        Some checks depend on things outside the YAML: where the file is (for
        relative paths), what "today" is, and which entry types exist (they
        are declared in Typst and read before validation).
    """

    input_file_path: pathlib.Path | None = None
    current_date: Any = None
    entry_types: Mapping[str, "EntryTypeDeclaration"] = field(default_factory=dict)
    entry_type_models: Mapping[str, type[pydantic.BaseModel]] = field(
        default_factory=dict
    )


def get_validation_context(info: pydantic.ValidationInfo) -> ValidationContext:
    """Extract the validation context, or an empty one if there is none.

    Args:
        info: Pydantic validation info.

    Returns:
        The validation context.
    """
    if isinstance(info.context, dict) and "context" in info.context:
        return cast(ValidationContext, info.context["context"])
    return ValidationContext()


def get_input_file_path(info: pydantic.ValidationInfo) -> pathlib.Path | None:
    """Extract input file path from validation context.

    Why:
        Relative paths in YAML (like photo references) must resolve relative
        to the input file's directory. Validators access this path via context
        to compute absolute paths during validation.

    Args:
        info: Pydantic validation info containing context.

    Returns:
        Input file path if available, otherwise None.
    """
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        if context.input_file_path:
            return context.input_file_path
    return None


def get_current_date(info: pydantic.ValidationInfo) -> Date:
    """Extract current date from validation context or default to today.

    Why:
        Date calculations (like months of experience) must use consistent
        reference dates. Users can override via settings.current_date for
        reproducible builds, otherwise defaults to today. The ``"today"``
        keyword is resolved to the actual current date. Invalid values fall
        back to today so the Settings model can report the error properly.

    Args:
        info: Pydantic validation info containing context.

    Returns:
        Current date from context or Date.today().
    """
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        if isinstance(context.current_date, Date):
            return context.current_date
        if context.current_date == "today":
            return Date.today()
    return Date.today()
