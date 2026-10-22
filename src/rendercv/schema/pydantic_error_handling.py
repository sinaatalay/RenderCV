import pathlib
import re
from typing import Any, cast

import pydantic
import pydantic_core
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from rendercv.exception import (
    OVERLAY_SOURCE_TO_YAML_SOURCE,
    OverlaySourceKey,
    RenderCVInternalError,
    RenderCVValidationError,
    YamlLocation,
    YamlSource,
)

from .models.custom_error_types import CustomPydanticErrorTypes
from .yaml_reader import read_yaml

error_dictionary = cast(
    dict[str, str],
    read_yaml(pathlib.Path(__file__).parent / "error_dictionary.yaml"),
)
unwanted_texts = ("value is not a valid email address: ", "Value error, ")
# Names pydantic adds to error locations for union branches and validators,
# like `str`, `list[str]`, or `function-after[...]`:
pydantic_location_artifact_pattern = re.compile(
    r"^(str|int|float|bool|none|url|email|date|datetime|model|"
    r"[\w-]+\[.*\]|constrained-[\w-]+|function-[\w-]+|tagged-union|literal)$"
)


def resolve_error_location(
    location: tuple[str | int, ...],
    input_dictionary: CommentedMap | dict[str, Any],
    *,
    is_missing: bool,
) -> tuple[str, ...]:
    """Remove pydantic's union-branch names from an error location.

    Why:
        Pydantic adds names like `str` or `list[str]` to locations of values
        that match one of several types. A location part that exists in the
        YAML is always kept, so user keys that happen to look like those names
        (a section called `list`, or `interests`) are never dropped.

    Args:
        location: The location pydantic reports.
        input_dictionary: The YAML the location points into.
        is_missing: Whether the error is about a missing field, whose name is
            not in the YAML.

    Returns:
        The location with only real keys and indices.
    """
    resolved: list[str] = []
    current: Any = input_dictionary
    for index, part in enumerate(location):
        is_last = index == len(location) - 1
        # Keys are compared as text, so a section titled `2024` (an int key) is found:
        keys = {str(key): key for key in current} if isinstance(current, dict) else {}
        if isinstance(current, dict) and str(part) in keys:
            resolved.append(str(part))
            current = current[keys[str(part)]]
        elif (
            isinstance(current, list) and isinstance(part, int) and part < len(current)
        ):
            resolved.append(str(part))
            current = current[part]
        elif pydantic_location_artifact_pattern.fullmatch(str(part)) and not (
            is_last and is_missing
        ):
            continue
        else:
            resolved.append(str(part))
            current = None
    return tuple(resolved)


def parse_plain_pydantic_error(
    plain_error: pydantic_core.ErrorDetails,
    input_dictionary: CommentedMap | dict[str, Any],
    overlay_sources: dict[str, CommentedMap] | None = None,
) -> RenderCVValidationError:
    """Transform raw Pydantic error into user-friendly validation error with YAML coordinates.

    Args:
        plain_error: Raw Pydantic validation error.
        input_dictionary: YAML dict with line/column metadata.
        overlay_sources: Per-section CommentedMaps from overlays (for correct coordinates).

    Returns:
        Structured error with location tuple, friendly message, and YAML coordinates.
    """
    for unwanted_text in unwanted_texts:
        plain_error["msg"] = plain_error["msg"].replace(unwanted_text, "")

    if "ctx" in plain_error:
        if "input" in plain_error["ctx"]:
            plain_error["input"] = plain_error["ctx"]["input"]

        if "loc" in plain_error["ctx"]:
            plain_error["loc"] = plain_error["ctx"]["loc"]

    location = resolve_error_location(
        plain_error["loc"],
        input_dictionary,
        is_missing=plain_error["type"] == "missing",
    )

    if location and "current_date" in location[-1]:
        plain_error["msg"] = (
            "This is not a valid `current_date`! Please use YYYY-MM-DD format or"
            ' "today".'
        )

    for old_error_message, new_error_message in error_dictionary.items():
        if old_error_message in plain_error["msg"]:
            plain_error["msg"] = new_error_message
            break

    if not plain_error["msg"].endswith((".", "?")):
        plain_error["msg"] += "."

    # Determine which YAML source this error came from and use the correct
    # CommentedMap for coordinate lookup
    yaml_source: YamlSource = "main_yaml_file"
    coord_dict: CommentedMap | dict[str, Any] = input_dictionary
    if overlay_sources and location and location[0] in overlay_sources:
        source_key = cast(OverlaySourceKey, location[0])
        yaml_source = OVERLAY_SOURCE_TO_YAML_SOURCE[source_key]
        coord_dict = overlay_sources[source_key]

    location_for_coords = (
        location if plain_error["type"] != "missing" else location[:-1]
    )

    return RenderCVValidationError(
        schema_location=location,
        yaml_location=(
            get_coordinates_of_a_key_in_a_yaml_object(
                coord_dict,
                location_for_coords,
            )
            if isinstance(coord_dict, CommentedMap)
            else None
        ),
        yaml_source=yaml_source,
        message=plain_error["msg"],
        input=(
            str(plain_error["input"])
            if not isinstance(plain_error["input"], dict | list)
            else "..."
        ),
    )


def parse_validation_errors(
    exception: pydantic.ValidationError,
    input_dictionary: CommentedMap | dict[str, Any],
    overlay_sources: dict[str, CommentedMap] | None = None,
) -> list[RenderCVValidationError]:
    """Extract all validation errors from Pydantic exception with deduplication.

    Args:
        exception: Pydantic validation exception.
        input_dictionary: YAML dict with location metadata.
        overlay_sources: Per-section CommentedMaps from overlays (for correct coordinates).

    Returns:
        Deduplicated list of user-friendly validation errors.
    """
    all_plain_errors = exception.errors()
    all_final_errors: list[RenderCVValidationError] = []

    for plain_error in all_plain_errors:
        if plain_error["type"] != CustomPydanticErrorTypes.entry_validation.value:
            all_final_errors.append(
                parse_plain_pydantic_error(
                    plain_error, input_dictionary, overlay_sources
                )
            )
            continue

        # Problems inside entries are reported one by one, each at its own place:
        if "ctx" not in plain_error or "caused_by" not in plain_error["ctx"]:
            raise RenderCVInternalError(
                "entry_validation error missing ctx or caused_by"
            )
        for plain_cause_error in plain_error["ctx"]["caused_by"]:
            plain_cause_error["loc"] = plain_error["loc"] + tuple(
                plain_cause_error["loc"]
            )
            all_final_errors.append(
                parse_plain_pydantic_error(
                    plain_cause_error, input_dictionary, overlay_sources
                )
            )

    # Remove duplicates from all_final_errors:
    error_locations = set()
    errors_without_duplicates = []
    for error in all_final_errors:
        schema_location = error.schema_location
        if schema_location not in error_locations:
            error_locations.add(schema_location)
            errors_without_duplicates.append(error)

    # A value that fits none of a union's types gets an error from each type.
    # When one type's errors point inside the value (`cv.email.1` for a list),
    # another type's error about the whole value (`cv.email`: "should be a
    # string") only confuses:
    return [
        error
        for error in errors_without_duplicates
        if not error.schema_location
        or not any(
            location[: len(error.schema_location)] == error.schema_location
            and len(location) > len(error.schema_location)
            for location in error_locations
            if location is not None
        )
    ]


def get_inner_yaml_object_from_its_key(
    yaml_object: Any,
    location_key: str,
) -> tuple[Any, YamlLocation] | None:
    """Navigate one level into YAML structure and extract coordinates.

    Why:
        Error locations are dotted paths like `cv.sections.education.0.degree`.
        Each traversal step must extract both the nested object and its exact
        source coordinates for error highlighting.

    Args:
        yaml_object: Current YAML object being traversed.
        location_key: Single key or list index as string.

    Returns:
        Tuple of nested object and ((start_line, start_col), (end_line, end_col)),
        or None if the YAML file doesn't have this key (for example, because a
        CLI override added it).
    """
    if isinstance(yaml_object, CommentedSeq):
        if not location_key.isdigit() or int(location_key) >= len(yaml_object):
            return None
        index = int(location_key)
        start_line, start_col = yaml_object.lc.data[index]
        return yaml_object[index], (
            (start_line + 1, start_col - 1),
            (start_line + 1, start_col),
        )
    if not isinstance(yaml_object, CommentedMap):
        return None
    # Keys are compared as text, so a section titled `2024` (an int key) is found:
    keys = {str(key): key for key in yaml_object}
    if location_key not in keys or keys[location_key] not in yaml_object.lc.data:
        return None
    key = keys[location_key]
    start_line, start_col, end_line, end_col = yaml_object.lc.data[key]
    return yaml_object[key], ((start_line + 1, start_col + 1), (end_line + 1, end_col))


def get_coordinates_of_a_key_in_a_yaml_object(
    yaml_object: CommentedMap, location: tuple[str, ...]
) -> YamlLocation | None:
    """Resolve dotted location path to exact YAML source coordinates.

    Why:
        Error tables must show users exactly which line/column contains
        the invalid value. Recursive traversal through CommentedMap's
        lc.data preserves coordinates at every nesting level. Parts of a
        location that aren't written in the YAML file (added by CLI overrides,
        or a missing field's name) point at their closest written parent.

    Example:
        ```py
        data = read_yaml(pathlib.Path("cv.yaml"))
        coords = get_coordinates_of_a_key_in_a_yaml_object(
            data, ("cv", "sections", "education", "0", "degree")
        )
        # coords = ((12, 4), (12, 10)) for line 12, columns 4-10
        ```

    Args:
        yaml_object: Root YAML object with location metadata.
        location: Path segments from root to target key.

    Returns:
        ((start_line, start_col), (end_line, end_col)) in 1-indexed coordinates,
        or None if not even the first part of the location is in the YAML file.
    """
    current_yaml_object: Any = yaml_object
    coordinates: YamlLocation | None = None
    for location_key in location:
        inner = get_inner_yaml_object_from_its_key(current_yaml_object, location_key)
        if inner is None:
            break
        current_yaml_object, coordinates = inner

    return coordinates
