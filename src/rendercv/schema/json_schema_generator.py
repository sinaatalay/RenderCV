import json
import pathlib
from collections.abc import Mapping
from typing import Any

import pydantic
import pydantic_core

from rendercv import __description__
from rendercv.renderer.typst_compiler import (
    TypstProject,
    read_entry_type_declarations,
)

from .models.cv.entry_types import (
    EntryTypeDeclaration,
    build_entry_type_models,
    entry_type_key,
    parse_entry_type_declarations,
)
from .models.rendercv_model import RenderCVModel


def entry_type_definition_name(entry_type_name: str) -> str:
    """Name an entry type's definition in the JSON Schema.

    Example:
        ```py
        entry_type_definition_name("one_line")  # "OneLineEntry"
        ```

    Args:
        entry_type_name: The entry type's name.

    Returns:
        The name in PascalCase, ending with "Entry".
    """
    words = entry_type_name.replace("-", "_").split("_")
    return "".join(word[:1].upper() + word[1:] for word in words) + "Entry"


def build_sections_json_schema(
    entry_types: Mapping[str, EntryTypeDeclaration],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the JSON Schema of `cv.sections` for the given entry types.

    Why:
        Entry types are declared in Typst, so the schema of a section's entries
        depends on them. Editors can then suggest and check every entry type's
        fields.

    Args:
        entry_types: The entry types.

    Returns:
        The schema of `cv.sections`, and the definitions it refers to.
    """
    definitions: dict[str, Any] = {}
    entry_schemas: list[dict[str, Any]] = []
    for name, model in build_entry_type_models(entry_types).items():
        schema = model.model_json_schema(ref_template="#/$defs/{model}")
        definitions.update(schema.pop("$defs", {}))
        schema["title"] = name
        schema["properties"] = {
            entry_type_key: {
                "const": name,
                "description": (
                    "The entry's type. Only needed when its fields fit several"
                    " entry types."
                ),
            },
            **schema.get("properties", {}),
        }
        schema["additionalProperties"] = False
        definition_name = entry_type_definition_name(name)
        definitions[definition_name] = schema
        entry_schemas.append({"$ref": f"#/$defs/{definition_name}"})
    if "paragraph" in entry_types:
        entry_schemas.append({"type": "string"})

    entries_schema = {"type": "array", "items": {"anyOf": entry_schemas}}
    sections_schema = {
        "type": "object",
        "title": "Sections",
        "description": (
            "The sections of your CV. Keys are section titles, and values are"
            " lists of entries, or mappings of subsection titles to lists of"
            " entries. Entry types are detected from their fields."
        ),
        "additionalProperties": {
            "anyOf": [
                entries_schema,
                {"type": "object", "additionalProperties": entries_schema},
            ]
        },
    }
    return sections_schema, definitions


def generate_json_schema(
    entry_types: Mapping[str, EntryTypeDeclaration] | None = None,
) -> dict[str, Any]:
    """Generate JSON Schema (Draft-07) from RenderCV Pydantic models.

    Why:
        IDEs and validators need machine-readable schema for autocompletion
        and real-time validation. Custom generator adds RenderCV-specific
        metadata like title, description, and canonical schema URL.

    Args:
        entry_types: The entry types sections may use. Without them, entries
            aren't checked.

    Returns:
        Draft-07 JSON Schema dictionary.
    """

    class RenderCVSchemaGenerator(pydantic.json_schema.GenerateJsonSchema):
        def generate(
            self,
            schema: pydantic_core.CoreSchema,
            mode: pydantic.json_schema.JsonSchemaMode = "validation",
        ) -> pydantic.json_schema.JsonSchemaValue:
            json_schema = super().generate(schema, mode=mode)
            json_schema["title"] = "RenderCV"
            json_schema["description"] = __description__
            json_schema["$id"] = (
                "https://raw.githubusercontent.com/rendercv/rendercv/main/schema.json"
            )
            json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"
            return json_schema

    schema = RenderCVModel.model_json_schema(schema_generator=RenderCVSchemaGenerator)
    if entry_types:
        sections_schema, definitions = build_sections_json_schema(entry_types)
        schema["$defs"] |= definitions
        schema["$defs"]["Sections"] = sections_schema
    return schema


def read_standard_entry_types() -> dict[str, EntryTypeDeclaration]:
    """Read the standard entry types from RenderCV's Typst package.

    Returns:
        The standard entry types.
    """
    project = TypstProject(root=pathlib.Path.cwd())
    return parse_entry_type_declarations(read_entry_type_declarations(project))


def generate_json_schema_file(json_schema_path: pathlib.Path) -> None:
    """Generate and save JSON Schema to file, with the standard entry types.

    Args:
        json_schema_path: Target file path for schema output.
    """
    schema = generate_json_schema(read_standard_entry_types())
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json + "\n", encoding="utf-8")
