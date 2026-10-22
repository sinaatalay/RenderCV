import dataclasses
import json
import re
from collections.abc import Mapping
from typing import Any

# Option paths whose values are Typst alignments rather than strings:
alignment_options = {
    "header.alignment",
    "typography.date_and_location_column_alignment",
}
# Colors Typst knows by name:
named_colors = {
    "black",
    "gray",
    "silver",
    "white",
    "navy",
    "blue",
    "aqua",
    "teal",
    "eastern",
    "purple",
    "fuchsia",
    "maroon",
    "red",
    "orange",
    "yellow",
    "olive",
    "green",
    "lime",
}
length_pattern = re.compile(r"^-?(\d+(\.\d*)?|\.\d+)(pt|mm|cm|in|em)$")
rgb_pattern = re.compile(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$")
hex_color_pattern = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
# Each expression ends with `;` so the text after it can't continue it (in
# Typst, `#date.year-#date.month` would read a field named `year-`):
date_placeholders: dict[str, str] = {
    "MONTH_NAME": "#locale.month_names.at(date.month - 1);",
    "MONTH_ABBREVIATION": "#locale.month_abbreviations.at(date.month - 1);",
    "MONTH_IN_TWO_DIGITS": "#str(date.month + 100).slice(1);",
    "MONTH": "#date.month;",
    "YEAR_IN_TWO_DIGITS": "#str(date.year).slice(-2);",
    "YEAR": "#date.year;",
}


@dataclasses.dataclass(frozen=True, kw_only=True)
class DesignMigration:
    """A RenderCV 2 design converted to a `design.typ`.

    Why:
        RenderCV 2 set the design in the YAML; RenderCV 3 designs are Typst
        files. Their option names are the same, so most designs convert
        exactly. What can't be converted is reported instead of dropped.
    """

    source: str
    warnings: tuple[str, ...]


def convert_color(value: str, path: str, warnings: list[str]) -> str | None:
    """Write a RenderCV 2 color as Typst.

    Args:
        value: The color, like "rgb(0, 79, 144)", "#004f90", or "red".
        path: The option's path, for warnings.
        warnings: Collects what couldn't be converted.

    Returns:
        The Typst color, or None if it couldn't be converted.
    """
    value = value.strip()
    if rgb_pattern.fullmatch(value):
        return re.sub(r"\s+", " ", value.replace(",", ", ").replace(",  ", ", "))
    if hex_color_pattern.fullmatch(value):
        return f"rgb({json.dumps(value)})"
    if value.lower() in named_colors:
        return value.lower()
    warnings.append(f"`design.{path}`: couldn't convert the color `{value}`.")
    return None


def convert_date_template(template: str) -> str:
    """Write a RenderCV 2 date template as a Typst function.

    Example:
        ```py
        convert_date_template("MONTH_NAME YEAR")
        # "(date, locale) => [#locale.month_names.at(date.month - 1); #date.year;]"
        ```

    Args:
        template: The template, like "MONTH_ABBREVIATION YEAR".

    Returns:
        A Typst function `(date, locale) => content`.
    """
    names = sorted(date_placeholders, key=lambda name: -len(name))
    pattern = re.compile("|".join(names))
    body = pattern.sub(lambda match: date_placeholders[match.group(0)], template)
    return f"(date, locale) => [{body}]"


def convert_value(value: Any, path: str, warnings: list[str]) -> str | None:
    """Write a RenderCV 2 design option's value as Typst.

    Args:
        value: The value from the YAML.
        path: The option's path, like "colors.name".
        warnings: Collects what couldn't be converted.

    Returns:
        The Typst value, or None to leave the option at its default.
    """
    if isinstance(value, Mapping):
        items = [
            (key, convert_value(item, f"{path}.{key}", warnings))
            for key, item in value.items()
        ]
        items = [(key, item) for key, item in items if item is not None]
        if not items:
            return None
        return "(" + ", ".join(f"{key}: {item}" for key, item in items) + ")"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        items = [json.dumps(str(item)) for item in value]
        return "(" + ", ".join(items) + ("," if len(items) == 1 else "") + ")"
    if value is None:
        return None
    text = str(value)
    if path.startswith("colors."):
        return convert_color(text, path, warnings)
    if path in alignment_options:
        return text if text in ("left", "center", "right") else None
    if length_pattern.fullmatch(text.strip()):
        return text.strip()
    return json.dumps(text, ensure_ascii=False)


def migrate_design(design: Mapping[str, Any], *, version: str) -> DesignMigration:
    """Convert a RenderCV 2 `design` field to a `design.typ`.

    Args:
        design: The `design` field from the YAML.
        version: The RenderCV Typst package version to import.

    Returns:
        The `design.typ` source and what couldn't be converted.
    """
    warnings: list[str] = []
    theme = str(design.get("theme", "classic"))
    built_in = {
        "classic",
        "moderncv",
        "sb2nov",
        "engineeringresumes",
        "engineeringclassic",
        "harvard",
        "ink",
        "ember",
        "opal",
    }
    if theme not in built_in:
        warnings.append(
            f"`design.theme` is the custom theme `{theme}`. Custom themes are Typst"
            " designs now; the migration starts from `classic`."
        )
        theme = "classic"

    options: dict[str, Any] = {
        key: value for key, value in design.items() if key not in ("theme", "templates")
    }
    templates = dict(design.get("templates") or {})
    converted_templates: dict[str, str] = {}
    if "single_date" in templates:
        converted_templates["single_date"] = convert_date_template(
            str(templates.pop("single_date"))
        )
    if "date_range" in templates:
        date_range = str(templates.pop("date_range"))
        converted_templates["date_range"] = (
            "(start, end) => ["
            + date_range.replace("START_DATE", "#start;").replace("END_DATE", "#end;")
            + "]"
        )
    for name in templates:
        where = (
            "the design's `templates` option"
            if name in ("footer", "top_note")
            else "the design's entry looks"
        )
        warnings.append(
            f"`design.templates.{name}`: templates with placeholders are Typst now."
            f" Write it as Typst in {where} in `design.typ` (see the docs)."
        )

    arguments = [
        f"  {key}: {converted},"
        for key, value in options.items()
        if (converted := convert_value(value, key, warnings)) is not None
    ]
    arguments += (
        [
            f"  templates: ({', '.join(f'{name}: {value}' for name, value in converted_templates.items())}),"
        ]
        if converted_templates
        else []
    )

    call = (
        f"designs.{theme}(\n" + "\n".join(arguments) + "\n)"
        if arguments
        else f"designs.{theme}()"
    )
    source = (
        "// Converted from a RenderCV 2 `design` field by `rendercv migrate`.\n"
        f'#import "@preview/rendercv:{version}": designs\n\n'
        f"#let design = {call}\n"
    )
    return DesignMigration(source=source, warnings=tuple(warnings))
