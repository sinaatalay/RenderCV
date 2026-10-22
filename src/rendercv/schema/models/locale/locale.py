import difflib
import functools
import pathlib
import re
from typing import Annotated, Any, Literal

import annotated_types as at
import pydantic
import pydantic_core

from ...yaml_reader import read_yaml
from ..base import BaseModelWithoutExtraKeys

locales_directory = (
    pathlib.Path(__file__).parent.parent.parent.parent / "data" / "locales"
)


# Built-in locales are named after their files, so listing them reads nothing:
available_locales: tuple[str, ...] = tuple(
    sorted(file.stem for file in locales_directory.glob("*.yaml"))
)


@functools.cache
def get_built_in_locale(language: str) -> dict[str, Any] | None:
    """Read a built-in locale's YAML file.

    Why:
        A locale is pure data, so each built-in one is one YAML file in
        `rendercv/data/locales/`. Adding a language is adding a file. Only
        the locale a CV uses is read, which keeps importing RenderCV fast
        (this matters most in the browser).

    Args:
        language: The language, like "german".

    Returns:
        The locale's values, or None if the language isn't built in.
    """
    if language not in available_locales:
        return None
    return dict(read_yaml(locales_directory / f"{language}.yaml"))


def get_built_in_locales() -> dict[str, dict[str, Any]]:
    """Read every built-in locale's YAML file.

    Returns:
        Language names mapped to their locale values.
    """
    return {
        language: locale
        for language in available_locales
        if (locale := get_built_in_locale(language)) is not None
    }


# No word boundaries: RenderCV 2 replaced placeholders anywhere, like in "בAREA".
old_phrase_placeholder_pattern = re.compile(r"DEGREE|AREA")


class Phrases(BaseModelWithoutExtraKeys):
    """Phrases that combine several fields, in the locale's word order."""

    degree_with_area: str = pydantic.Field(
        description=(
            "How a degree and a field of study are written together, as Typst"
            " markup where `#degree` and `#area` are the two fields. For example,"
            ' `"#degree in #area"` writes "PhD in Computer Science".'
        ),
        examples=["#degree in #area", "#degree en #area"],
    )

    @pydantic.field_validator("degree_with_area", mode="before")
    @classmethod
    def convert_old_placeholders(cls, value: Any) -> Any:
        """Accept RenderCV 2's `DEGREE in AREA` form and convert it to Typst.

        Args:
            value: The phrase from the YAML.

        Returns:
            The phrase with `DEGREE` and `AREA` written as `#degree;` and
            `#area;` (the `;` ends the Typst expression, so text right after it,
            like "AREAszakon", stays text).
        """
        if isinstance(value, str) and "#" not in value:
            return old_phrase_placeholder_pattern.sub(
                lambda match: "#" + match.group(0).lower() + ";", value
            )
        return value


type MonthNames = Annotated[list[str], at.Len(min_length=12, max_length=12)]


class Locale(BaseModelWithoutExtraKeys):
    """The words and formats of the CV's language.

    Why:
        Dates, "present", and phrases like "PhD in Computer Science" depend on
        the language. Choosing a built-in language fills in all of them;
        anything can still be changed, and any language can be defined.
    """

    # A built-in `language` fills in every other field, so the JSON Schema
    # requires none of them (`locale: {language: german}` is complete):
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    language: str = pydantic.Field(
        default="english",
        description=(
            "The language of the CV. Choosing a built-in language fills in all"
            " other fields; for another language, provide all fields."
        ),
        json_schema_extra={"examples": list(available_locales)},
    )
    iso_code: str = pydantic.Field(
        description=(
            "The language's ISO 639 code, like `en` or `de`. Used for"
            " hyphenation and accessibility."
        ),
        examples=["en", "de", "tr"],
    )
    direction: Literal["ltr", "rtl"] = pydantic.Field(
        default="ltr",
        description="The writing direction: `ltr` (left to right) or `rtl`.",
    )
    last_updated: str = pydantic.Field(description='Translation of "Last updated in".')
    present: str = pydantic.Field(description='Translation of "present".')
    month: str = pydantic.Field(description='Translation of "month".')
    months: str = pydantic.Field(description='Translation of "months".')
    year: str = pydantic.Field(description='Translation of "year".')
    years: str = pydantic.Field(description='Translation of "years".')
    phrases: Phrases
    month_abbreviations: MonthNames = pydantic.Field(
        description="Month abbreviations, January to December."
    )
    month_names: MonthNames = pydantic.Field(
        description="Month names, January to December."
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def fill_in_built_in_language(cls, data: Any) -> Any:
        """Start from the built-in locale of the chosen language, if there is one.

        Args:
            data: The `locale` mapping from the YAML.

        Returns:
            The built-in locale's values, overridden by the YAML's.
        """
        if not isinstance(data, dict):
            return data
        language = data.get("language", "english")
        # Values of the wrong type are left for field validation to report:
        built_in = get_built_in_locale(language) if isinstance(language, str) else None
        if built_in is None:
            missing = [
                name
                for name, field in cls.model_fields.items()
                if field.is_required() and name not in data
            ]
            if isinstance(language, str) and missing:
                suggestion = difflib.get_close_matches(language, available_locales, n=1)
                hint = f" Did you mean `{suggestion[0]}`?" if suggestion else ""
                raise pydantic_core.PydanticCustomError(
                    "rendercv_locale",
                    "There is no built-in language `{language}`.{hint} For another"
                    " language, give all the locale's fields ({missing}).",
                    {"language": language, "hint": hint, "missing": ", ".join(missing)},
                )
            return data
        phrases = data.get("phrases") or {}
        if not isinstance(phrases, dict):
            return {**built_in, **data}
        return {**built_in, **data, "phrases": {**built_in["phrases"], **phrases}}


def default_locale() -> Locale:
    """Return the English locale."""
    return Locale.model_validate({"language": "english"})
