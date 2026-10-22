import pathlib
from collections.abc import Mapping
from typing import Any

import pydantic
import pytest

from rendercv.schema.models.cv.cv import Cv, connection_fields
from rendercv.schema.models.cv.entry_types import (
    EntryTypeDeclaration,
    PhoneValue,
    validate_phone,
)
from rendercv.schema.models.validation_context import ValidationContext


@pytest.fixture
def validation_context(
    tmp_path: pathlib.Path,
    standard_entry_types: Mapping[str, EntryTypeDeclaration],
    standard_entry_type_models: Mapping[str, type[pydantic.BaseModel]],
) -> dict[str, ValidationContext]:
    return {
        "context": ValidationContext(
            input_file_path=tmp_path / "cv.yaml",
            entry_types=standard_entry_types,
            entry_type_models=standard_entry_type_models,
        )
    }


def test_connection_fields() -> None:
    assert connection_fields == (
        "location",
        "email",
        "phone",
        "website",
        "social_networks",
        "custom_connections",
    )


class TestCv:
    def test_everything_is_optional(self) -> None:
        cv = Cv()

        assert cv.model_dump() == dict.fromkeys(Cv.model_fields)

    def test_validates_every_header_field(
        self, tmp_path: pathlib.Path, validation_context: dict[str, ValidationContext]
    ) -> None:
        (tmp_path / "photo.jpg").touch()

        cv = Cv.model_validate(
            {
                "name": "John Doe",
                "headline": "Engineer",
                "location": "Istanbul, Türkiye",
                "email": "john@example.com",
                "photo": "photo.jpg",
                "phone": "+905419999999",
                "website": "https://example.com",
                "social_networks": [{"network": "GitHub", "username": "johndoe"}],
                "custom_connections": [
                    {"placeholder": "Book a call", "fontawesome_icon": "calendar"}
                ],
                "sections": {"summary": ["Hello."]},
            },
            context=validation_context,
        )

        assert cv.name == "John Doe"
        assert cv.photo == tmp_path / "photo.jpg"
        assert cv.phone == PhoneValue(
            e164="+905419999999",
            international="+90 541 999 99 99",
            national="0541 999 99 99",
            uri="tel:+90-541-999-99-99",
        )
        assert cv.website == "https://example.com"
        assert cv.social_networks is not None
        assert cv.social_networks[0].url == "https://github.com/johndoe"
        assert cv.custom_connections is not None
        assert cv.custom_connections[0].url is None
        assert cv.sections is not None
        assert cv.sections[0].title == "Summary"

    @pytest.mark.parametrize(
        ("field", "value", "expected_value"),
        [
            (
                "email",
                ["a@example.com", "b@example.com"],
                ["a@example.com", "b@example.com"],
            ),
            (
                "website",
                ["https://a.com", "https://b.com/"],
                ["https://a.com", "https://b.com/"],
            ),
            ("name", 2024, "2024"),
        ],
    )
    def test_accepts_lists_and_numbers(
        self, field: str, value: Any, expected_value: Any
    ) -> None:
        assert getattr(Cv.model_validate({field: value}), field) == expected_value

    def test_accepts_a_list_of_phone_numbers(self) -> None:
        cv = Cv.model_validate({"phone": ["+14155550100", "+442079460958"]})

        assert cv.phone == [
            validate_phone("+14155550100"),
            validate_phone("+442079460958"),
        ]

    def test_accepts_a_photo_url(self) -> None:
        cv = Cv.model_validate({"photo": "https://example.com/photo.jpg"})

        assert str(cv.photo) == "https://example.com/photo.jpg"

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("email", "not an email"),
            ("phone", "not a phone"),
            ("website", "example.com"),
            ("photo", "missing.jpg"),
            ("social_networks", [{"network": "GitHub"}]),
            ("custom_connections", [{"placeholder": "x"}]),
            ("nmae", "John Doe"),
        ],
    )
    def test_rejects_invalid_values(
        self, validation_context: dict[str, ValidationContext], field: str, value: Any
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Cv.model_validate({field: value}, context=validation_context)

        assert exc_info.value.errors()[0]["loc"][0] == field

    def test_validates_sections_with_the_entry_types(
        self, validation_context: dict[str, ValidationContext]
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Cv.model_validate(
                {"sections": {"experience": [{"compnay": "ACME", "position": "X"}]}},
                context=validation_context,
            )

        (cause,) = exc_info.value.errors()[0]["ctx"]["caused_by"]
        assert cause["loc"] == ("experience", 0, "compnay")
