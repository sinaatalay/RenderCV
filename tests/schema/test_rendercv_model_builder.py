import pathlib
from collections.abc import Mapping
from datetime import date as Date
from typing import Any, cast

import pytest
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    RenderCVValidationError,
)
from rendercv.schema.models.cv.entry_types import Entry, EntryTypeDeclaration
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary,
    build_rendercv_dictionary_and_model,
    build_rendercv_model_from_commented_map,
    get_yaml_error_location,
    read_yaml_with_validation_errors,
)

type EntryTypes = Mapping[str, EntryTypeDeclaration]

main_yaml = """cv:
  name: John Doe
  sections:
    experience:
      - company: ACME
        position: Engineer
locale:
  language: english
settings:
  current_date: 2024-06-15
  render_command:
    pdf_path: original.pdf
"""


def overlay_arguments(keyword: str, value: Any) -> BuildRendercvModelArguments:
    return cast(BuildRendercvModelArguments, {keyword: value})


def validation_errors_of(
    yaml: str,
    entry_types: EntryTypes | None = None,
    **kwargs: Any,
) -> list[RenderCVValidationError]:
    with pytest.raises(RenderCVUserValidationError) as exc_info:
        build_rendercv_dictionary_and_model(yaml, entry_types=entry_types, **kwargs)
    return exc_info.value.validation_errors


class TestGetYamlErrorLocation:
    def test_returns_none_without_marks(self) -> None:
        assert get_yaml_error_location(ruamel.yaml.YAMLError()) is None

    def test_returns_one_indexed_coordinates(self) -> None:
        with pytest.raises(ruamel.yaml.YAMLError) as exc_info:
            ruamel.yaml.YAML().load("cv:\n  name: John\n   phone: 123\n")

        assert get_yaml_error_location(exc_info.value) == ((3, 9), (3, 9))


class TestReadYamlWithValidationErrors:
    def test_reads_valid_yaml(self) -> None:
        result = read_yaml_with_validation_errors("cv:\n  name: A\n", "main_yaml_file")

        assert isinstance(result, CommentedMap)

    @pytest.mark.parametrize(
        "yaml_source", ["main_yaml_file", "locale_yaml_file", "settings_yaml_file"]
    )
    def test_reports_syntax_errors_as_validation_errors(self, yaml_source: Any) -> None:
        with pytest.raises(RenderCVUserValidationError) as exc_info:
            read_yaml_with_validation_errors(
                "cv:\n  name: John\n   phone: 123\n", yaml_source
            )

        (error,) = exc_info.value.validation_errors
        assert error.schema_location is None
        assert error.yaml_source == yaml_source
        assert error.yaml_location == ((3, 9), (3, 9))
        assert error.message.startswith("This is not a valid YAML file. ")
        assert error.message.endswith(".")
        assert error.input == "..."


class TestBuildRendercvDictionary:
    def test_reads_the_yaml(self) -> None:
        dictionary, overlay_sources = build_rendercv_dictionary(main_yaml)

        assert dictionary["cv"]["name"] == "John Doe"
        assert overlay_sources == {}

    @pytest.mark.parametrize(
        "yaml",
        [
            "cv:\n  name: A\n",
            "cv:\n  name: A\nsettings:\n",
            "settings:\n  pdf_title: T\n",
        ],
    )
    def test_always_has_settings_and_render_command(self, yaml: str) -> None:
        dictionary, _ = build_rendercv_dictionary(yaml)

        assert dictionary["settings"]["render_command"] == {}

    @pytest.mark.parametrize(
        ("keyword", "overlay", "key"),
        [
            ("locale_yaml_file", "locale:\n  language: turkish\n", "locale"),
            (
                "settings_yaml_file",
                "settings:\n  render_command:\n    pdf_path: overlay.pdf\n",
                "settings",
            ),
        ],
    )
    def test_overlays_replace_the_main_section(
        self, keyword: str, overlay: str, key: str
    ) -> None:
        dictionary, overlay_sources = build_rendercv_dictionary(
            main_yaml, **overlay_arguments(keyword, overlay)
        )

        assert dictionary[key] == ruamel.yaml.YAML().load(overlay)[key]
        assert dictionary["cv"]["name"] == "John Doe"
        assert list(overlay_sources) == [key]
        # Replaced, not merged:
        if key == "settings":
            assert "current_date" not in dictionary["settings"]

    @pytest.mark.parametrize("keyword", ["locale_yaml_file", "settings_yaml_file"])
    def test_empty_overlays_are_ignored(self, keyword: str) -> None:
        dictionary, overlay_sources = build_rendercv_dictionary(
            main_yaml, **overlay_arguments(keyword, None)
        )

        assert dictionary["locale"]["language"] == "english"
        assert overlay_sources == {}

    @pytest.mark.parametrize(
        ("keyword", "overlay", "expected_source"),
        [
            ("locale_yaml_file", "language: turkish\n", "locale_yaml_file"),
            ("settings_yaml_file", "- a\n- b\n", "settings_yaml_file"),
            (
                "locale_yaml_file",
                "locale:\n  language: x\n   present: y\n",
                "locale_yaml_file",
            ),
        ],
    )
    def test_reports_broken_overlay_files(
        self, keyword: str, overlay: str, expected_source: str
    ) -> None:
        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_dictionary(main_yaml, **overlay_arguments(keyword, overlay))

        (error,) = exc_info.value.validation_errors
        assert error.yaml_source == expected_source

    def test_overlay_without_its_key_says_so(self) -> None:
        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_dictionary(main_yaml, locale_yaml_file="language: x\n")

        assert exc_info.value.validation_errors[0].message == (
            "This file should have a top-level `locale` field, like `locale:` on its"
            " first line."
        )

    @pytest.mark.parametrize(
        ("keyword", "value"),
        [
            ("output_folder", "out"),
            ("typst_path", "custom.typ"),
            ("pdf_path", "output.pdf"),
            ("markdown_path", "output.md"),
            ("html_path", "output.html"),
            ("png_path", "output.png"),
            ("dont_generate_typst", True),
            ("dont_generate_html", True),
            ("dont_generate_markdown", True),
            ("dont_generate_pdf", True),
            ("dont_generate_png", True),
        ],
    )
    def test_render_options_go_into_render_command(
        self, keyword: str, value: Any
    ) -> None:
        dictionary, _ = build_rendercv_dictionary(
            main_yaml, **overlay_arguments(keyword, value)
        )

        assert dictionary["settings"]["render_command"][keyword] == value

    @pytest.mark.parametrize("value", [None, False, ""])
    def test_unset_render_options_keep_the_yaml_values(self, value: Any) -> None:
        dictionary, _ = build_rendercv_dictionary(
            main_yaml, pdf_path=value, dont_generate_pdf=value
        )

        assert dictionary["settings"]["render_command"] == {"pdf_path": "original.pdf"}

    def test_applies_overrides_last(self) -> None:
        dictionary, _ = build_rendercv_dictionary(
            main_yaml,
            locale_yaml_file="locale:\n  language: english\n",
            pdf_path="cli.pdf",
            overrides={
                "cv.name": "Jane Doe",
                "cv.sections.experience.0.company": "Initech",
                "locale.language": "turkish",
                "settings.render_command.pdf_path": "override.pdf",
            },
        )

        assert dictionary["cv"]["name"] == "Jane Doe"
        assert dictionary["cv"]["sections"]["experience"][0]["company"] == "Initech"
        assert dictionary["locale"]["language"] == "turkish"
        assert dictionary["settings"]["render_command"]["pdf_path"] == "override.pdf"

    def test_reports_invalid_override_paths(self) -> None:
        with pytest.raises(RenderCVUserError, match="is not an integer"):
            build_rendercv_dictionary(
                main_yaml, overrides={"cv.sections.experience.first": "x"}
            )


class TestBuildRendercvModelFromCommentedMap:
    def test_builds_the_model(self, standard_entry_types: EntryTypes) -> None:
        dictionary, _ = build_rendercv_dictionary(main_yaml)

        model = build_rendercv_model_from_commented_map(
            dictionary, entry_types=standard_entry_types
        )

        assert model.cv.name == "John Doe"
        assert model.settings.current_date == Date(2024, 6, 15)
        assert model.cv.sections is not None
        assert model.cv.sections[0].entries == (
            Entry(
                type_name="experience",
                values={
                    "company": "ACME",
                    "position": "Engineer",
                    **dict.fromkeys(
                        [
                            "date",
                            "start_date",
                            "end_date",
                            "location",
                            "summary",
                            "highlights",
                        ]
                    ),
                },
            ),
        )

    def test_accepts_plain_dictionaries(self) -> None:
        model = build_rendercv_model_from_commented_map({"cv": {"name": "John"}})

        assert model.cv.name == "John"

    def test_resolves_paths_relative_to_the_input_file(
        self, tmp_path: pathlib.Path
    ) -> None:
        (tmp_path / "photo.jpg").touch()

        model = build_rendercv_model_from_commented_map(
            {"cv": {"photo": "photo.jpg"}}, input_file_path=tmp_path / "cv.yaml"
        )

        assert model.cv.photo == tmp_path / "photo.jpg"

    def test_entries_need_entry_types(self) -> None:
        dictionary, _ = build_rendercv_dictionary(main_yaml)

        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_model_from_commented_map(dictionary)

        (error,) = exc_info.value.validation_errors
        assert error.schema_location == ("cv", "sections", "experience", "0")
        assert "There are no entry types" in error.message

    def test_reports_errors_with_yaml_locations(self) -> None:
        dictionary, _ = build_rendercv_dictionary("cv:\n  name: A\n  emal: a@b.co\n")

        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_model_from_commented_map(dictionary)

        (error,) = exc_info.value.validation_errors
        assert error.schema_location == ("cv", "emal")
        assert error.yaml_location == ((3, 3), (3, 8))
        assert (
            error.message == "This field is unknown for this object. Please remove it."
        )

    def test_error_message_lists_every_problem(self) -> None:
        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_model_from_commented_map(
                {"cv": {"emal": "x", "website": "y"}}
            )

        assert str(exc_info.value) == (
            "cv.website: This is not a valid URL.\n"
            "cv.emal: This field is unknown for this object. Please remove it."
        )


class TestBuildRendercvDictionaryAndModel:
    def test_builds_the_dictionary_and_the_model(
        self, standard_entry_types: EntryTypes
    ) -> None:
        dictionary, model = build_rendercv_dictionary_and_model(
            main_yaml,
            entry_types=standard_entry_types,
            locale_yaml_file="locale:\n  language: turkish\n",
            pdf_path="custom.pdf",
            overrides={"cv.name": "Jane Doe"},
        )

        assert dictionary["cv"]["name"] == "Jane Doe"
        assert model.cv.name == "Jane Doe"
        assert model.locale.language == "turkish"
        assert model.settings.render_command.pdf_path.name == "custom.pdf"

    def test_input_file_path_resolves_output_paths(
        self, input_file_path: pathlib.Path, standard_entry_types: EntryTypes
    ) -> None:
        _, model = build_rendercv_dictionary_and_model(
            input_file_path.read_text(encoding="utf-8"),
            input_file_path=input_file_path,
            entry_types=standard_entry_types,
            output_folder="out",
        )

        assert model.settings.render_command.output_folder == (
            input_file_path.parent / "out"
        )

    @pytest.mark.parametrize(
        ("yaml", "message"),
        [
            ("", "The input file is empty!"),
            ("- a\n- b\n", "should be a mapping"),
            ("just text\n", "should be a mapping"),
        ],
    )
    def test_rejects_yaml_that_is_not_a_mapping(self, yaml: str, message: str) -> None:
        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_dictionary_and_model(yaml)

        (error,) = exc_info.value.validation_errors
        assert message in error.message
        assert error.yaml_source == "main_yaml_file"

    def test_rendercv_2_design_field_asks_for_migration(self) -> None:
        (error,) = validation_errors_of(
            "cv:\n  name: John\ndesign:\n  theme: classic\n"
        )

        assert error.schema_location == ("design",)
        assert error.yaml_location == ((3, 1), (4, 2))
        assert "Run `rendercv migrate`" in error.message

    @pytest.mark.parametrize(
        "invalid_date", ["todady", "not-a-date", "2024-13-01", "yesterday"]
    )
    def test_invalid_current_date_is_explained(self, invalid_date: str) -> None:
        (error,) = validation_errors_of(
            f"cv:\n  name: John\nsettings:\n  current_date: {invalid_date}\n"
        )

        assert error.schema_location == ("settings", "current_date")
        assert error.yaml_location == ((4, 3), (4, 16))
        assert "YYYY-MM-DD" in error.message

    def test_today_is_a_valid_current_date(self) -> None:
        _, model = build_rendercv_dictionary_and_model(
            "settings:\n  current_date: today\n"
        )

        assert model.settings.current_date == "today"

    def test_entry_errors_point_to_their_lines(
        self, standard_entry_types: EntryTypes
    ) -> None:
        errors = validation_errors_of(
            "cv:\n"
            "  sections:\n"
            "    experience:\n"
            "      - company: ACME\n"
            "        positon: Engineer\n"
            "    education:\n"
            "      - institution: MIT\n"
            "        area: CS\n"
            "        start_date: 2020-13\n",
            standard_entry_types,
        )

        assert [(error.schema_location, error.yaml_location) for error in errors] == [
            (("cv", "sections", "experience", "0", "positon"), ((5, 9), (5, 17))),
            (("cv", "sections", "education", "0", "start_date"), ((9, 9), (9, 20))),
        ]

    def test_overlay_errors_point_into_the_overlay_file(
        self, standard_entry_types: EntryTypes
    ) -> None:
        (error,) = validation_errors_of(
            main_yaml,
            standard_entry_types,
            locale_yaml_file="# The locale.\nlocale:\n  language: english\n  present: [1]\n",
        )

        assert error.yaml_source == "locale_yaml_file"
        assert error.schema_location == ("locale", "present")
        assert error.yaml_location == ((4, 3), (4, 11))

    @pytest.mark.parametrize(
        ("overrides", "expected_location", "expected_yaml_location"),
        [
            # The override replaced a value written in the YAML:
            (
                {"cv.name": "[1]", "cv.website": "bad"},
                ("cv", "website"),
                ((1, 1), (2, 2)),
            ),
            # The override added keys the YAML doesn't have:
            (
                {"cv.phone": "not a phone"},
                ("cv", "phone"),
                ((1, 1), (2, 2)),
            ),
            (
                {"cv.sections.new.0": "x"},
                ("cv", "sections", "new", "0"),
                ((3, 3), (4, 4)),
            ),
            (
                {"settings.render_command.unknown": "x"},
                ("settings", "render_command", "unknown"),
                ((11, 3), (12, 4)),
            ),
            ({"design.theme": "classic"}, ("design",), None),
        ],
    )
    def test_errors_in_overridden_values_point_to_the_closest_yaml_line(
        self,
        standard_entry_types: EntryTypes,
        overrides: dict[str, str],
        expected_location: tuple[str, ...],
        expected_yaml_location: Any,
    ) -> None:
        # Such locations used to crash the error table (#758):
        (error,) = validation_errors_of(
            main_yaml, standard_entry_types, overrides=overrides
        )

        assert error.schema_location == expected_location
        assert error.yaml_location == expected_yaml_location

    def test_numeric_section_titles_point_to_their_lines(
        self, standard_entry_types: EntryTypes
    ) -> None:
        (error,) = validation_errors_of(
            "cv:\n"
            "  sections:\n"
            "    publications:\n"
            "      2024:\n"
            "        - title: Paper\n"
            "          authors: Not a list\n",
            standard_entry_types,
        )

        assert error.schema_location == (
            "cv",
            "sections",
            "publications",
            "2024",
            "0",
            "authors",
        )
        assert error.yaml_location == ((6, 11), (6, 19))

    @pytest.mark.parametrize("section_title", ["interests", "list", "str", "int"])
    def test_section_titles_like_type_names_are_kept(
        self, standard_entry_types: EntryTypes, section_title: str
    ) -> None:
        (error,) = validation_errors_of(
            f"cv:\n  sections:\n    {section_title}:\n      - label: A\n        detial: B\n",
            standard_entry_types,
        )

        assert error.schema_location == (
            "cv",
            "sections",
            section_title,
            "0",
            "detial",
        )
        assert error.message.endswith("Did you mean `details`?")
