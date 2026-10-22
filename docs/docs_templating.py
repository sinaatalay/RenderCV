"""Variables for the documentation pages, read from RenderCV's own code.

`mkdocs-macros-plugin` runs `define_env` before building the docs. Pages use the
variables with `<< variable >>` and `{$ for ... $}` blocks, so lists of designs,
locales, social networks, entry types, and design options always match the code.
"""

import io
import pathlib
import re
import textwrap
from typing import Any

import rendercv_fonts
import ruamel.yaml

from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import (
    FieldDeclaration,
    build_entry_type_models,
    validate_entry,
)
from rendercv.schema.models.cv.social_network import get_available_social_networks
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_entries_file,
    get_built_in_design_names,
)
from rendercv.schema.yaml_reader import read_yaml

repository_root = pathlib.Path(__file__).parent.parent
designs_directory = repository_root / "typst" / "designs"
sample_entries_path = repository_root / "docs" / "user_guide" / "sample_entries.yaml"

# The entry figures in `docs/assets/images/<design>/` are named after RenderCV 2's
# entry types:
figure_names: dict[str, str] = {
    "education": "education_entry",
    "experience": "experience_entry",
    "normal": "normal_entry",
    "publication": "publication_entry",
    "one_line": "one_line_entry",
    "bullet": "bullet_entry",
    "numbered": "numbered_entry",
    "reversed_numbered": "reversed_numbered_entry",
    "paragraph": "text_entry",
}


def to_yaml(value: Any) -> str:
    """Write a value as YAML, the way the docs show it."""
    yaml = ruamel.yaml.YAML()
    yaml.width = 70
    yaml.indent(mapping=2, sequence=4, offset=2)
    with io.StringIO() as stream:
        yaml.dump(value, stream)
        text = textwrap.dedent(stream.getvalue())
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"


def describe_kind(field: FieldDeclaration) -> str:
    """Describe a field's kind for the entry type tables, like "list of markdown"."""
    if field.kind == "list":
        return f"list of {field.of or 'markdown'}"
    if field.kind == "choice":
        return "one of " + ", ".join(f"`{choice}`" for choice in field.choices or ())
    if field.kind == "date" and field.allow_text:
        return "date or text"
    return field.kind


def read_typst_dictionary(path: pathlib.Path, name: str) -> str:
    """Read a top-level `#let name = (...)` dictionary's source from a Typst file.

    Args:
        path: The Typst file.
        name: The name of the dictionary.

    Returns:
        The source, from `#let` to the closing parenthesis.
    """
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"^#let {re.escape(name)} = \(\n.*?^\)$", source, re.S | re.M)
    if match is None:
        message = f"`#let {name} = (...)` is not in {path}."
        raise ValueError(message)
    return match.group(0)


def define_env(env: Any) -> None:
    """Define the variables the documentation pages use.

    Args:
        env: The `mkdocs-macros-plugin` environment.
    """
    designs = get_built_in_design_names()
    env.variables["design_names"] = list(designs)
    env.variables["design_count"] = len(designs)
    env.variables["available_designs"] = ", ".join(
        f"`{design}`" if design != "classic" else "`classic` (default)"
        for design in designs
    )
    env.variables["available_locales"] = ", ".join(
        f"`{locale}`" if locale != "english" else "`english` (default)"
        for locale in available_locales
    )
    env.variables["locale_count"] = len(available_locales)
    env.variables["available_social_networks"] = ", ".join(
        f"`{network}`" for network in get_available_social_networks()
    )
    env.variables["available_font_families"] = ", ".join(
        f"`{font}`"
        for font in sorted(rendercv_fonts.available_font_families)
        if not font.startswith("Font Awesome")
    )

    # The standard entry types, with a validated sample of each:
    entry_types = read_standard_entry_types()
    models = build_entry_type_models(entry_types)
    samples = read_yaml(sample_entries_path)
    showcase: dict[str, dict[str, Any]] = {}
    for name, entry_type in entry_types.items():
        sample = samples[name]
        entry, errors = validate_entry(sample, entry_types, models)
        if entry is None or entry.type_name != name:
            message = f"The sample `{name}` entry is invalid: {errors}"
            raise ValueError(message)
        showcase[name] = {
            "doc": entry_type.doc,
            "fields_table": "\n".join(
                [
                    "| Field | Kind | Required | Description |",
                    "| ----- | ---- | -------- | ----------- |",
                    *(
                        f"| `{field_name}` | {describe_kind(field)} |"
                        f" {'No' if field.optional else 'Yes'} |"
                        f" {(field.doc or '').replace('|', '\\|')} |"
                        for field_name, field in entry_type.fields.items()
                    ),
                ]
            ),
            "yaml": to_yaml([sample]),
            "figures": [
                {
                    "design": design,
                    "path": f"../assets/images/{design}/{figure_names[name]}.png",
                }
                for design in designs
            ],
        }
    env.variables["entry_types"] = showcase
    env.variables["entry_type_count"] = len(showcase)

    # Design options, straight from the Typst sources:
    env.variables["engine_defaults"] = read_typst_dictionary(
        designs_directory / "engine.typ", "defaults"
    )
    env.variables["design_defaults"] = {
        design: read_typst_dictionary(
            designs_directory / f"{design}.typ", f"{design}-defaults"
        )
        for design in designs
        if design != "classic"
    }
    env.variables["sample_design_file"] = create_sample_design_file("classic")
    env.variables["sample_entries_file"] = create_sample_entries_file()
