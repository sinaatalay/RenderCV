import json
import pathlib
from collections.abc import Iterator, Mapping
from typing import Any

import pytest

from rendercv import __description__
from rendercv.schema.json_schema_generator import (
    build_sections_json_schema,
    entry_type_definition_name,
    generate_json_schema,
    generate_json_schema_file,
    read_standard_entry_types,
)
from rendercv.schema.models.cv.entry_types import (
    EntryTypeDeclaration,
    parse_entry_type_declarations,
)
from rendercv.schema.sample_generator import create_sample_yaml_input_file
from rendercv.schema.yaml_reader import read_yaml

type EntryTypes = Mapping[str, EntryTypeDeclaration]


def references_in(schema: Any) -> Iterator[str]:
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "$ref":
                yield value
            else:
                yield from references_in(value)
    elif isinstance(schema, list):
        for item in schema:
            yield from references_in(item)


@pytest.mark.parametrize(
    ("entry_type_name", "expected_definition_name"),
    [
        ("normal", "NormalEntry"),
        ("one_line", "OneLineEntry"),
        ("reversed_numbered", "ReversedNumberedEntry"),
        ("conference-talk", "ConferenceTalkEntry"),
        ("talk", "TalkEntry"),
    ],
)
def test_entry_type_definition_name(
    entry_type_name: str, expected_definition_name: str
) -> None:
    assert entry_type_definition_name(entry_type_name) == expected_definition_name


def test_read_standard_entry_types(standard_entry_types: EntryTypes) -> None:
    assert read_standard_entry_types() == standard_entry_types


class TestBuildSectionsJsonSchema:
    def test_defines_every_entry_type(self, standard_entry_types: EntryTypes) -> None:
        _, definitions = build_sections_json_schema(standard_entry_types)

        for name, entry_type in standard_entry_types.items():
            definition = definitions[entry_type_definition_name(name)]
            assert definition["title"] == name
            assert definition["description"] == entry_type.doc
            assert definition["additionalProperties"] is False
            assert set(definition.get("required", [])) == entry_type.required_fields
            assert list(definition["properties"]) == ["type", *entry_type.fields]

    def test_type_is_a_constant_of_the_entry_type_name(
        self, standard_entry_types: EntryTypes
    ) -> None:
        _, definitions = build_sections_json_schema(standard_entry_types)

        assert definitions["ExperienceEntry"]["properties"]["type"]["const"] == (
            "experience"
        )
        assert "type" not in definitions["ExperienceEntry"].get("required", [])

    def test_entries_are_entry_types_or_paragraph_text(
        self, standard_entry_types: EntryTypes
    ) -> None:
        sections_schema, _ = build_sections_json_schema(standard_entry_types)

        entries_schema = sections_schema["additionalProperties"]["anyOf"][0]
        assert entries_schema["type"] == "array"
        assert entries_schema["items"]["anyOf"] == [
            *(
                {"$ref": f"#/$defs/{entry_type_definition_name(name)}"}
                for name in standard_entry_types
            ),
            {"type": "string"},
        ]
        # Subsections hold the same entries:
        assert sections_schema["additionalProperties"]["anyOf"][1] == {
            "type": "object",
            "additionalProperties": entries_schema,
        }

    def test_text_is_not_an_entry_without_a_paragraph_type(self) -> None:
        entry_types = parse_entry_type_declarations(
            {"talk": {"doc": None, "fields": {"title": {"kind": "markdown"}}}}
        )

        sections_schema, _ = build_sections_json_schema(entry_types)

        assert sections_schema["additionalProperties"]["anyOf"][0]["items"] == {
            "anyOf": [{"$ref": "#/$defs/TalkEntry"}]
        }

    def test_describes_field_kinds(self, standard_entry_types: EntryTypes) -> None:
        _, definitions = build_sections_json_schema(standard_entry_types)

        publication = definitions["PublicationEntry"]["properties"]
        assert publication["authors"]["type"] == "array"
        assert {"pattern": "10\\..+", "type": "string"} in publication["doi"]["anyOf"]
        assert {"type": "string"} in publication["date"]["anyOf"]
        normal = definitions["NormalEntry"]["properties"]
        assert {"type": "string"} not in normal["start_date"]["anyOf"]
        assert normal["highlights"]["anyOf"][0] == {
            "type": "array",
            "items": {"type": "string"},
        }


class TestGenerateJsonSchema:
    def test_describes_rendercv(self) -> None:
        schema = generate_json_schema()

        assert schema["title"] == "RenderCV"
        assert schema["description"] == __description__
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["$id"].endswith("/schema.json")
        assert set(schema["properties"]) == {"cv", "locale", "settings"}
        assert "design" not in schema["properties"]

    def test_without_entry_types_sections_are_not_checked(self) -> None:
        schema = generate_json_schema()

        assert "NormalEntry" not in schema["$defs"]
        assert schema["$defs"]["Sections"]["additionalProperties"]["anyOf"][0] == {
            "type": "array"
        }

    def test_sections_use_the_entry_types(
        self, standard_entry_types: EntryTypes
    ) -> None:
        schema = generate_json_schema(standard_entry_types)

        assert schema["$defs"]["Cv"]["properties"]["sections"]["anyOf"][0] == {
            "$ref": "#/$defs/Sections"
        }
        assert (
            schema["$defs"]["Sections"]
            == (build_sections_json_schema(standard_entry_types)[0])
        )

    def test_every_reference_is_defined(self, standard_entry_types: EntryTypes) -> None:
        schema = generate_json_schema(standard_entry_types)

        references = set(references_in(schema))

        assert references
        assert {reference.removeprefix("#/$defs/") for reference in references} <= set(
            schema["$defs"]
        )

    def test_sample_entries_fit_exactly_one_entry_type(
        self, standard_entry_types: EntryTypes
    ) -> None:
        schema = generate_json_schema(standard_entry_types)
        sample = read_yaml(create_sample_yaml_input_file())

        for section in sample["cv"]["sections"].values():
            for entry in section:
                if isinstance(entry, str):
                    continue
                fitting = [
                    name
                    for name in standard_entry_types
                    if set(
                        schema["$defs"][entry_type_definition_name(name)].get(
                            "required", []
                        )
                    )
                    <= set(entry)
                    <= set(
                        schema["$defs"][entry_type_definition_name(name)]["properties"]
                    )
                ]
                assert len(fitting) == 1, entry

    def test_validates_the_sample_cv(self, standard_entry_types: EntryTypes) -> None:
        # `jsonschema` is not a RenderCV dependency:
        jsonschema = pytest.importorskip("jsonschema")
        schema = generate_json_schema(standard_entry_types)
        sample = json.loads(json.dumps(read_yaml(create_sample_yaml_input_file())))

        jsonschema.validate(sample, schema)


def test_generate_json_schema_file(
    tmp_path: pathlib.Path, standard_entry_types: EntryTypes
) -> None:
    schema_file = tmp_path / "schema.json"

    generate_json_schema_file(schema_file)

    text = schema_file.read_text(encoding="utf-8")
    assert text.endswith("}\n")
    assert json.loads(text) == json.loads(
        json.dumps(generate_json_schema(standard_entry_types))
    )
