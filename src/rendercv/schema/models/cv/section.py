import dataclasses
from collections.abc import Mapping
from typing import Annotated, Any

import pydantic
import pydantic_core

from ..custom_error_types import CustomPydanticErrorTypes
from ..validation_context import get_validation_context
from .entry_types import Entry, validate_entry


@dataclasses.dataclass(frozen=True, kw_only=True)
class Section:
    """A validated section: a title, and entries or subsections.

    Why:
        A CV is sections of entries, optionally grouped into subsections.
        Nothing else about a CV's structure is special, so this is all the
        structure the rest of RenderCV needs.
    """

    title: str
    key: str
    entries: tuple[Entry, ...] = ()
    subsections: tuple["Section", ...] = ()


def dictionary_key_to_proper_section_title(key: str) -> str:
    """Convert snake_case section key to title case with proper capitalization.

    Why:
        Users write `education_and_training` in YAML for readability. Rendering
        requires "Education and Training" with proper title case rules (lowercase
        articles/prepositions).

    Example:
        ```py
        title = dictionary_key_to_proper_section_title("education_and_training")
        # Returns "Education and Training"
        ```

    Args:
        key: Section key from YAML.

    Returns:
        Properly capitalized section title.
    """
    # If there is either a space or an uppercase letter in the key, return it as is.
    if " " in key or any(letter.isupper() for letter in key):
        return key

    words_not_capitalized_in_a_title = {
        "a",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "from",
        "if",
        "in",
        "into",
        "like",
        "near",
        "nor",
        "of",
        "off",
        "on",
        "onto",
        "or",
        "over",
        "so",
        "than",
        "that",
        "to",
        "upon",
        "when",
        "with",
        "yet",
    }

    return " ".join(
        word if word in words_not_capitalized_in_a_title else word.capitalize()
        for word in key.replace("_", " ").split(" ")
    )


def section_key(title: str) -> str:
    """Turn a section title into the key designs refer to sections by.

    Example:
        ```py
        section_key("Education and Training")  # "education_and_training"
        ```

    Args:
        title: The section's title.

    Returns:
        The title in lowercase with spaces replaced by underscores.
    """
    return title.lower().replace(" ", "_")


def validate_sections(value: Any, info: pydantic.ValidationInfo) -> list[Section]:
    """Validate all sections, collecting every problem in every entry.

    Why:
        A section is a list of entries, or a mapping of subsection titles to
        lists of entries. Entry types come from Typst, so each entry is checked
        against them here. All problems are reported together, each at its own
        place in the YAML.

    Args:
        value: The `sections` mapping from the YAML.
        info: Validation info, whose context holds the entry types.

    Returns:
        The validated sections, in the order they were written.
    """
    if not isinstance(value, Mapping):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "Sections should be a mapping of section titles to lists of entries.",
        )
    context = get_validation_context(info)
    errors: list[pydantic_core.ErrorDetails] = []

    def validate_entries(
        entries: Any, location: tuple[str | int, ...]
    ) -> tuple[Entry, ...]:
        if entries is None:
            return ()
        if not isinstance(entries, list):
            errors.append(
                {
                    "type": "rendercv_section",
                    "loc": location,
                    "msg": (
                        "A section should be a list of entries, or a mapping of"
                        " subsection titles to lists of entries."
                    ),
                    "input": "...",
                }
            )
            return ()
        validated: list[Entry] = []
        for index, raw_entry in enumerate(entries):
            entry, entry_errors = validate_entry(
                raw_entry, context.entry_types, context.entry_type_models
            )
            for error in entry_errors:
                errors.append(error | {"loc": (*location, index, *error["loc"])})
            if entry is not None:
                validated.append(entry)
        return tuple(validated)

    sections: list[Section] = []
    for key, section_value in value.items():
        title = dictionary_key_to_proper_section_title(str(key))
        if isinstance(section_value, Mapping):
            subsections = tuple(
                Section(
                    title=dictionary_key_to_proper_section_title(str(sub_key)),
                    key=section_key(
                        dictionary_key_to_proper_section_title(str(sub_key))
                    ),
                    entries=validate_entries(sub_value, (key, sub_key)),
                )
                for sub_key, sub_value in section_value.items()
            )
            sections.append(
                Section(title=title, key=section_key(title), subsections=subsections)
            )
        else:
            sections.append(
                Section(
                    title=title,
                    key=section_key(title),
                    entries=validate_entries(section_value, (key,)),
                )
            )

    if errors:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.entry_validation.value,
            "There are problems with the entries.",
            {"caused_by": errors},
        )
    return sections


type Sections = Annotated[
    list[Section],
    pydantic.PlainValidator(validate_sections),
    pydantic.WithJsonSchema(
        {
            "type": "object",
            "description": (
                "The sections of your CV. Keys are section titles, and values are"
                " lists of entries, or mappings of subsection titles to lists of"
                " entries. Entry types are detected from their fields."
            ),
            "additionalProperties": {
                "anyOf": [
                    {"type": "array"},
                    {"type": "object", "additionalProperties": {"type": "array"}},
                ]
            },
        }
    ),
]
