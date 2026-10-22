from typing import Any

import pydantic
import pytest

from rendercv.schema.models.cv.custom_connection import CustomConnection


class TestCustomConnection:
    def test_url_is_optional(self) -> None:
        connection = CustomConnection.model_validate(
            {"placeholder": "Book a call", "fontawesome_icon": "calendar-days"}
        )

        assert connection.url is None

    def test_accepts_a_url(self) -> None:
        connection = CustomConnection.model_validate(
            {
                "placeholder": "Book a call",
                "fontawesome_icon": "calendar-days",
                "url": "https://cal.com/johndoe",
            }
        )

        assert str(connection.url) == "https://cal.com/johndoe"

    @pytest.mark.parametrize(
        ("value", "expected_error_location"),
        [
            ({"fontawesome_icon": "calendar"}, ("placeholder",)),
            ({"placeholder": "Call"}, ("fontawesome_icon",)),
            (
                {"placeholder": "Call", "fontawesome_icon": "calendar", "url": "cal"},
                ("url",),
            ),
            (
                {"placeholder": "Call", "fontawesome_icon": "calendar", "icon": "x"},
                ("icon",),
            ),
        ],
    )
    def test_rejects_invalid_connections(
        self, value: dict[str, Any], expected_error_location: tuple[str, ...]
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            CustomConnection.model_validate(value)

        assert exc_info.value.errors()[0]["loc"] == expected_error_location
