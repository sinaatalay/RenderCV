import dataclasses
import pathlib
from collections.abc import Mapping
from typing import Any

import pydantic
import pydantic_core
import pytest
import ruamel.yaml
from hypothesis import given
from hypothesis import strategies as st

from rendercv.exception import RenderCVInternalError, RenderCVValidationError
from rendercv.schema.models.custom_error_types import CustomPydanticErrorTypes
from rendercv.schema.models.cv.entry_types import EntryTypeDeclaration
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.pydantic_error_handling import (
    error_dictionary,
    get_coordinates_of_a_key_in_a_yaml_object,
    get_inner_yaml_object_from_its_key,
    parse_plain_pydantic_error,
    parse_validation_errors,
    resolve_error_location,
)
from rendercv.schema.yaml_reader import read_yaml

type EntryTypes = Mapping[str, EntryTypeDeclaration]
type EntryTypeModels = Mapping[str, type[pydantic.BaseModel]]


@pytest.fixture
def context(
    standard_entry_types: EntryTypes, standard_entry_type_models: EntryTypeModels
) -> dict[str, ValidationContext]:
    return {
        "context": ValidationContext(
            entry_types=standard_entry_types,
            entry_type_models=standard_entry_type_models,
        )
    }


def plain_error(**fields: Any) -> pydantic_core.ErrorDetails:
    return {"type": "value_error", "loc": (), "msg": "Message.", "input": "x"} | fields  # ty: ignore[invalid-return-type]


def validation_error_of(
    model: type[pydantic.BaseModel], data: Any
) -> pydantic.ValidationError:
    with pytest.raises(pydantic.ValidationError) as exc_info:
        model.model_validate(data)
    return exc_info.value


class RaisesEntryValidationErrorWithoutCauses(pydantic.BaseModel):
    value: Any

    @pydantic.field_validator("value")
    @classmethod
    def fail(cls, value: Any) -> Any:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.entry_validation.value,
            "Problems with {value}.",
            {"value": value},
        )


class TestResolveErrorLocation:
    @pytest.mark.parametrize(
        ("location", "expected_location"),
        [
            (("cv", "email", "list[email]", 1), ("cv", "email", "1")),
            (("cv", "email", "str"), ("cv", "email")),
            (("cv", "phone", "function-plain[validate_phone()]"), ("cv", "phone")),
            (("cv", "photo", "url"), ("cv", "photo")),
            (("settings", "current_date", "date"), ("settings", "current_date")),
            (("cv", "amount", "int"), ("cv", "amount")),
            (("cv", "level", "literal['a','b']"), ("cv", "level")),
            (("cv", "code", "constrained-str"), ("cv", "code")),
            (("cv", "x", "tagged-union[A,B]"), ("cv", "x")),
        ],
    )
    def test_drops_pydantic_union_branch_names(
        self, location: tuple[str | int, ...], expected_location: tuple[str, ...]
    ) -> None:
        input_dictionary = {
            "cv": {"email": ["a", "b"], "phone": "x", "photo": "x", "amount": "x"},
            "settings": {"current_date": "x"},
        }

        assert (
            resolve_error_location(location, input_dictionary, is_missing=False)
            == expected_location
        )

    @pytest.mark.parametrize("key", ["list", "str", "int", "date", "url", "interests"])
    def test_keeps_real_keys_that_look_like_branch_names(self, key: str) -> None:
        input_dictionary = {"cv": {"sections": {key: [{"label": "A"}]}}}

        assert resolve_error_location(
            ("cv", "sections", key, 0, "label"), input_dictionary, is_missing=False
        ) == ("cv", "sections", key, "0", "label")

    def test_keeps_the_name_of_a_missing_field(self) -> None:
        input_dictionary = {"cv": {"sections": {"s": [{"a": "b"}]}}}

        assert resolve_error_location(
            ("cv", "sections", "s", 0, "date"), input_dictionary, is_missing=True
        ) == ("cv", "sections", "s", "0", "date")

    def test_keeps_parts_that_are_not_in_the_yaml(self) -> None:
        # Like keys added by CLI overrides:
        assert resolve_error_location(
            ("cv", "phone", "extra"), {"cv": {}}, is_missing=False
        ) == ("cv", "phone", "extra")

    def test_keeps_indices_past_the_end_of_a_list(self) -> None:
        assert resolve_error_location(
            ("items", 5), {"items": ["a"]}, is_missing=False
        ) == ("items", "5")

    def test_finds_keys_that_are_not_text(self) -> None:
        input_dictionary = {"sections": {2024: [{"title": "Paper"}]}}

        assert resolve_error_location(
            ("sections", 2024, 0, "title", "str"), input_dictionary, is_missing=False
        ) == ("sections", "2024", "0", "title")

    @given(
        keys=st.lists(
            st.one_of(
                st.sampled_from(["str", "int", "list", "date", "url", "model"]),
                st.from_regex(r"[a-z_]{1,8}", fullmatch=True),
            ),
            min_size=1,
            max_size=6,
        )
    )
    def test_locations_of_real_keys_are_kept(self, keys: list[str]) -> None:
        input_dictionary: dict[str, Any] = {}
        current = input_dictionary
        for key in keys:
            current[key] = {}
            current = current[key]

        assert resolve_error_location(
            tuple(keys), input_dictionary, is_missing=False
        ) == tuple(keys)


class TestParsePlainPydanticError:
    @pytest.mark.parametrize(
        ("message", "expected_message"),
        [
            ("Value error, Something is wrong.", "Something is wrong."),
            (
                "value is not a valid email address: An email address must have an"
                " @-sign.",
                "An email address must have an @-sign.",
            ),
            ("Field required", "This field is required."),
            ("Input should be a valid URL, empty host", "This is not a valid URL."),
            (
                "String should match pattern '10\\..+'",
                'A DOI always starts with "10.". For example,'
                ' "10.1109/TASC.2023.3340648".',
            ),
            ("No period", "No period."),
            ("Did you mean this?", "Did you mean this?"),
        ],
    )
    def test_rewrites_messages_for_users(
        self, message: str, expected_message: str
    ) -> None:
        error = parse_plain_pydantic_error(plain_error(msg=message), {})

        assert error.message == expected_message

    def test_error_dictionary_has_every_message_ending_in_a_period(self) -> None:
        assert error_dictionary
        assert all(message.endswith(".") for message in error_dictionary.values())

    def test_explains_invalid_current_dates(self) -> None:
        error = parse_plain_pydantic_error(
            plain_error(loc=("settings", "current_date", "date"), msg="Bad."),
            {"settings": {"current_date": "x"}},
        )

        assert error.schema_location == ("settings", "current_date")
        assert error.message == (
            'This is not a valid `current_date`! Please use YYYY-MM-DD format or "today".'
        )

    def test_context_can_set_the_location_and_input(self) -> None:
        error = parse_plain_pydantic_error(
            plain_error(ctx={"loc": ("design",), "input": "..."}),
            {"design": {"theme": "classic"}},
        )

        assert error.schema_location == ("design",)
        assert error.input == "..."

    @pytest.mark.parametrize(
        ("input_value", "expected_input"),
        [("text", "text"), (5, "5"), (None, "None"), ({"a": 1}, "..."), ([1], "...")],
    )
    def test_shows_inputs_briefly(self, input_value: Any, expected_input: str) -> None:
        error = parse_plain_pydantic_error(plain_error(input=input_value), {})

        assert error.input == expected_input

    def test_plain_dictionaries_have_no_yaml_location(self) -> None:
        error = parse_plain_pydantic_error(plain_error(loc=("cv",)), {"cv": {}})

        assert error.yaml_location is None
        assert error.yaml_source == "main_yaml_file"

    def test_missing_fields_point_to_their_parent(self) -> None:
        yaml = read_yaml("cv:\n  custom_connections:\n    - placeholder: x\n")

        error = parse_plain_pydantic_error(
            plain_error(
                type="missing",
                loc=("cv", "custom_connections", 0, "fontawesome_icon"),
                msg="Field required",
            ),
            yaml,
        )

        assert error.schema_location == (
            "cv",
            "custom_connections",
            "0",
            "fontawesome_icon",
        )
        assert error.yaml_location == ((3, 5), (3, 6))
        assert error.message == "This field is required."

    def test_errors_in_overlays_point_into_the_overlay(self) -> None:
        main = read_yaml("cv:\n  name: John\n")
        overlay = read_yaml("# Locale\n\nlocale:\n  present: [1]\n")
        main["locale"] = overlay["locale"]

        error = parse_plain_pydantic_error(
            plain_error(loc=("locale", "present")), main, {"locale": overlay}
        )

        assert error.yaml_source == "locale_yaml_file"
        assert error.yaml_location == ((4, 3), (4, 11))


class TestParseValidationErrors:
    def test_matches_the_expected_errors_of_a_wrong_input(
        self,
        testdata_dir: pathlib.Path,
        update_testdata: bool,
        context: dict[str, ValidationContext],
    ) -> None:
        wrong_input_path = testdata_dir / "wrong_input.yaml"
        wrong_input = read_yaml(wrong_input_path)
        expected_errors_path = testdata_dir / "expected_errors.yaml"

        with pytest.raises(pydantic.ValidationError) as exc_info:
            RenderCVModel.model_validate(
                wrong_input,
                context={
                    "context": dataclasses.replace(
                        context["context"], input_file_path=wrong_input_path
                    )
                },
            )
        errors = [
            error_as_yaml_data(error)
            for error in parse_validation_errors(exc_info.value, wrong_input)
        ]

        if update_testdata:
            yaml = ruamel.yaml.YAML()
            yaml.width = 4096
            with expected_errors_path.open("w", encoding="utf-8") as file:
                yaml.dump({"expected_errors": errors}, file)

        expected_errors = ruamel.yaml.YAML(typ="safe").load(
            expected_errors_path.read_text(encoding="utf-8")
        )["expected_errors"]
        assert errors == expected_errors

    def test_reports_every_entry_problem_at_its_place(
        self, context: dict[str, ValidationContext]
    ) -> None:
        yaml = read_yaml(
            "cv:\n"
            "  sections:\n"
            "    a:\n"
            "      - bulet: x\n"
            "    b:\n"
            "      c:\n"
            "        - name: x\n"
            "          date: 2020-13\n"
        )

        with pytest.raises(pydantic.ValidationError) as exc_info:
            RenderCVModel.model_validate(yaml, context=context)
        errors = parse_validation_errors(exc_info.value, yaml)

        assert [(error.schema_location, error.yaml_location) for error in errors] == [
            (("cv", "sections", "a", "0", "bulet"), ((4, 9), (4, 15))),
            (("cv", "sections", "b", "c", "0", "date"), ((8, 11), (8, 16))),
        ]

    def test_entry_validation_errors_need_their_causes(self) -> None:
        error = validation_error_of(
            RaisesEntryValidationErrorWithoutCauses, {"value": 1}
        )

        with pytest.raises(RenderCVInternalError, match="missing ctx or caused_by"):
            parse_validation_errors(error, {"value": 1})

    def test_reports_one_error_per_location(self) -> None:
        # `current_date` fits neither the date nor "today", so pydantic reports
        # both; the user needs to hear it once:
        error = validation_error_of(RenderCVModel, {"settings": {"current_date": "x"}})

        assert len(error.errors()) == 2
        assert [
            parsed.schema_location
            for parsed in parse_validation_errors(
                error, {"settings": {"current_date": "x"}}
            )
        ] == [("settings", "current_date")]

    @pytest.mark.parametrize(
        ("field", "value", "expected_location", "expected_message"),
        [
            (
                "email",
                ["a@example.com", "bad"],
                ("cv", "email", "1"),
                "An email address must have an @-sign.",
            ),
            (
                "phone",
                ["+14155550100", "bad"],
                ("cv", "phone", "1"),
                "This is not a valid phone number.",
            ),
            (
                "website",
                ["https://example.com", "bad"],
                ("cv", "website", "1"),
                "This is not a valid URL.",
            ),
            ("email", "bad", ("cv", "email"), "An email address must have an @-sign."),
        ],
    )
    def test_reports_the_problem_inside_a_list_not_the_type_mismatch(
        self,
        field: str,
        value: Any,
        expected_location: tuple[str, ...],
        expected_message: str,
    ) -> None:
        data = {"cv": {field: value}}
        error = validation_error_of(RenderCVModel, data)

        (parsed,) = parse_validation_errors(error, data)

        assert parsed.schema_location == expected_location
        assert parsed.message == expected_message


class TestGetInnerYamlObjectFromItsKey:
    def test_returns_the_value_and_coordinates_of_a_key(self) -> None:
        yaml = read_yaml("name: John\nage: 30\n")

        assert get_inner_yaml_object_from_its_key(yaml, "age") == (30, ((2, 1), (2, 5)))

    def test_returns_the_item_and_coordinates_of_an_index(self) -> None:
        items = read_yaml("items:\n  - first\n  - second\n")["items"]

        assert get_inner_yaml_object_from_its_key(items, "1") == (
            "second",
            ((3, 3), (3, 4)),
        )

    def test_finds_keys_that_are_not_text(self) -> None:
        yaml = read_yaml("2024: Paper\n")

        assert get_inner_yaml_object_from_its_key(yaml, "2024") == (
            "Paper",
            ((1, 1), (1, 6)),
        )

    @pytest.mark.parametrize(
        ("yaml", "key"),
        [
            ("name: John\n", "nonexistent"),
            ("- a\n- b\n", "5"),
            ("- a\n- b\n", "name"),
            ("name: John\n", "0"),
        ],
    )
    def test_returns_none_for_keys_not_in_the_yaml(self, yaml: str, key: str) -> None:
        assert (
            get_inner_yaml_object_from_its_key(ruamel.yaml.YAML().load(yaml), key)
            is None
        )

    def test_returns_none_for_keys_added_after_reading(self) -> None:
        yaml = read_yaml("name: John\n")
        yaml["phone"] = "123"

        assert get_inner_yaml_object_from_its_key(yaml, "phone") is None

    @pytest.mark.parametrize("yaml_object", [{"name": "John"}, "text", None])
    def test_returns_none_for_objects_without_coordinates(
        self, yaml_object: Any
    ) -> None:
        assert get_inner_yaml_object_from_its_key(yaml_object, "name") is None


class TestGetCoordinatesOfAKeyInAYamlObject:
    yaml = "cv:\n  sections:\n    education:\n      - institution: MIT\n"

    def test_returns_the_coordinates_of_the_location(self) -> None:
        assert get_coordinates_of_a_key_in_a_yaml_object(
            read_yaml(self.yaml), ("cv", "sections", "education", "0", "institution")
        ) == ((4, 9), (4, 21))

    @pytest.mark.parametrize(
        ("location", "expected_coordinates"),
        [
            (("cv", "sections", "education", "0", "area"), ((4, 7), (4, 8))),
            (("cv", "sections", "education", "3"), ((3, 5), (4, 6))),
            (("cv", "phone", "0"), ((1, 1), (2, 2))),
        ],
    )
    def test_points_to_the_closest_part_in_the_yaml(
        self, location: tuple[str, ...], expected_coordinates: Any
    ) -> None:
        assert (
            get_coordinates_of_a_key_in_a_yaml_object(read_yaml(self.yaml), location)
            == expected_coordinates
        )

    @pytest.mark.parametrize("location", [(), ("design",)])
    def test_returns_none_when_nothing_is_in_the_yaml(
        self, location: tuple[str, ...]
    ) -> None:
        assert (
            get_coordinates_of_a_key_in_a_yaml_object(read_yaml(self.yaml), location)
            is None
        )


def error_as_yaml_data(error: RenderCVValidationError) -> dict[str, Any]:
    data = dataclasses.asdict(error)
    data["schema_location"] = list(error.schema_location or ())
    data["yaml_location"] = (
        [list(part) for part in error.yaml_location] if error.yaml_location else None
    )
    return data
