import datetime
from typing import Any

import pydantic
import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.schema.models.settings.render_command import RenderCommand
from rendercv.schema.models.settings.settings import Settings


class TestSettings:
    def test_defaults(self) -> None:
        settings = Settings()

        assert settings.current_date == "today"
        assert settings.render_command == RenderCommand()
        assert settings.bold_keywords == []
        assert settings.pdf_title == "NAME - CV"

    @pytest.mark.parametrize(
        ("value", "expected_current_date"),
        [
            ("today", "today"),
            (datetime.date(2024, 6, 15), datetime.date(2024, 6, 15)),
            ("2024-06-15", datetime.date(2024, 6, 15)),
        ],
    )
    def test_current_date(self, value: Any, expected_current_date: Any) -> None:
        assert Settings(current_date=value).current_date == expected_current_date

    @pytest.mark.parametrize("value", ["not-a-date", "todady", "2024-13-01", 5.5])
    def test_rejects_invalid_current_dates(self, value: Any) -> None:
        with pytest.raises(pydantic.ValidationError):
            Settings(current_date=value)

    @pytest.mark.parametrize(
        ("value", "expected_date"),
        [
            ("today", datetime.date.today()),
            (datetime.date(2024, 6, 15), datetime.date(2024, 6, 15)),
        ],
    )
    def test_resolved_current_date(
        self, value: Any, expected_date: datetime.date
    ) -> None:
        assert Settings(current_date=value).resolved_current_date == expected_date

    def test_pdf_title(self) -> None:
        settings = Settings(pdf_title="NAME - Resume YEAR")

        assert settings.pdf_title == "NAME - Resume YEAR"

    def test_removes_duplicate_bold_keywords(self) -> None:
        settings = Settings(bold_keywords=["Python", "Java", "Python", "C++", "Java"])

        assert settings.bold_keywords == ["Python", "Java", "C++"]

    def test_rejects_unknown_fields(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            Settings.model_validate({"design": "design.typ"})

    @given(
        keywords=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda text: text.strip()),
            max_size=20,
        )
    )
    def test_deduplication_preserves_order(self, keywords: list[str]) -> None:
        settings = Settings(bold_keywords=keywords)

        assert settings.bold_keywords == list(dict.fromkeys(keywords))
