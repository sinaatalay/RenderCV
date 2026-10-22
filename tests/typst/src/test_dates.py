from collections.abc import Callable
from typing import Any

import pytest

from rendercv.schema.models.locale.locale import Locale

type TypstValue = Callable[..., Any]
type TypstText = Callable[..., str]

prelude = '#import "/src/dates.typ": *'


def locale(language: str = "english", **words: str) -> dict[str, Any]:
    return Locale.model_validate({"language": language, **words}).model_dump()


def date(value: int | str | None) -> dict[str, Any] | None:
    """Write a date the way RenderCV sends it: 2020, "2020-05", "present"."""
    if value is None:
        return None
    if value == "present":
        return {"present": True}
    parts = [int(part) for part in str(value).split("-")]
    return dict(zip(("year", "month", "day"), parts, strict=False))


def normalized(name: str) -> str:
    return f"normalize-date(data.{name})"


class TestNormalizeDate:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (
                {"year": 2020},
                {
                    "year": 2020,
                    "month": None,
                    "day": None,
                    "present": False,
                    "text": None,
                },
            ),
            (
                {"year": 2020, "month": 5, "day": 3},
                {"year": 2020, "month": 5, "day": 3, "present": False, "text": None},
            ),
            (
                {"present": True},
                {
                    "year": None,
                    "month": None,
                    "day": None,
                    "present": True,
                    "text": None,
                },
            ),
        ],
    )
    def test_fills_in_missing_keys(
        self, typst_value: TypstValue, value: dict[str, Any], expected: dict[str, Any]
    ) -> None:
        assert (
            typst_value(normalized("date"), prelude=prelude, data={"date": value})
            == expected
        )

    def test_turns_text_into_content(self, typst_text: TypstText) -> None:
        text = typst_text(
            "normalize-date(data.date).text",
            prelude=prelude,
            data={"date": {"text": ["Fall ", {"strong": ["2023"]}]}},
        )

        assert text == "Fall 2023"

    def test_keeps_none(self, typst_value: TypstValue) -> None:
        assert typst_value("normalize-date(none)", prelude=prelude) is None


class TestFormatDate:
    @pytest.mark.parametrize(
        ("value", "language", "expected"),
        [
            ({"year": 2020}, "english", "2020"),
            ({"year": 2023, "month": 9}, "english", "Sept 2023"),
            ({"year": 2023, "month": 9, "day": 14}, "english", "Sept 2023"),
            ({"present": True}, "english", "present"),
            ({"text": ["Fall 2023"]}, "english", "Fall 2023"),
            ({"year": 2020, "month": 3}, "german", "Mär 2020"),
            ({"present": True}, "german", "gegenwärtig"),
            ({"year": 2020, "month": 8}, "turkish", "Ağu 2020"),
        ],
    )
    def test_writes_dates_in_the_locale(
        self,
        typst_text: TypstText,
        value: dict[str, Any],
        language: str,
        expected: str,
    ) -> None:
        text = typst_text(
            "format-date(normalize-date(data.date), data.locale)",
            prelude=prelude,
            data={"date": value, "locale": locale(language)},
        )

        assert text == expected

    def test_uses_a_custom_format(self, typst_text: TypstText) -> None:
        text = typst_text(
            "format-date(normalize-date(data.date), data.locale, format: (date,"
            " locale) => [#date.month/#date.year])",
            prelude=prelude,
            data={"date": {"year": 2023, "month": 9}, "locale": locale()},
        )

        assert text == "9/2023"

    def test_keeps_none(self, typst_value: TypstValue) -> None:
        assert (
            typst_value(
                "format-date(none, data.locale)",
                prelude=prelude,
                data={"locale": locale()},
            )
            is None
        )


def test_month_abbreviation_and_year(typst_text: TypstText) -> None:
    text = typst_text(
        "month-abbreviation-and-year(normalize-date(data.date), data.locale)",
        prelude=prelude,
        data={"date": {"year": 2024, "month": 12}, "locale": locale()},
    )

    assert text == "Dec 2024"


class TestFormatDates:
    def format(
        self,
        typst_text: TypstText,
        *,
        single: int | str | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        language: str = "english",
        arguments: str = "",
    ) -> str:
        return typst_text(
            "format-dates(data.locale, date: normalize-date(data.date), start:"
            " normalize-date(data.start), end: normalize-date(data.end)"
            f"{arguments})",
            prelude=prelude,
            data={
                "date": date(single),
                "start": date(start),
                "end": date(end),
                "locale": locale(language),
            },
        )

    def test_prefers_the_single_date(self, typst_text: TypstText) -> None:
        assert (
            self.format(typst_text, single="2021-05", start=2019, end=2020)
            == "May 2021"
        )

    def test_writes_a_range(self, typst_text: TypstText) -> None:
        assert (
            self.format(typst_text, start="2019-09", end="2021-06")
            == "Sept 2019 – June 2021"
        )

    def test_writes_an_ongoing_range(self, typst_text: TypstText) -> None:
        assert self.format(typst_text, start=2019) == "2019 – present"
        assert self.format(typst_text, start=2019, end="present") == "2019 – present"

    def test_writes_only_an_end_date_as_a_single_date(
        self, typst_text: TypstText
    ) -> None:
        assert self.format(typst_text, end="2020-02") == "Feb 2020"

    def test_writes_nothing_without_dates(self, typst_text: TypstText) -> None:
        assert self.format(typst_text) == ""

    def test_uses_the_locale(self, typst_text: TypstText) -> None:
        assert (
            self.format(typst_text, start="2019-03", language="german")
            == "Mär 2019 – gegenwärtig"
        )

    def test_uses_custom_format_and_range(self, typst_text: TypstText) -> None:
        text = self.format(
            typst_text,
            start="2019-03",
            end="2020-04",
            arguments=(
                ", format: (date, locale) => [#date.month.#date.year], range:"
                " (start, end) => [from #start to #end]"
            ),
        )

        assert text == "from 3.2019 to 4.2020"


class TestFormatTimeSpan:
    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            # Years only:
            (2020, 2021, "1 year"),
            (2020, 2022, "2 years"),
            (2020, 2024, "4 years"),
            (2020, 2020, "1 year"),
            ("2020-10-10", 2022, "2 years"),
            (2022, "2023-10-10", "1 year"),
            (2020, "present", "5 years"),
            # Years and months:
            ("2020-01-01", "2021-01-01", "1 year 1 month"),
            ("2020-01-01", "2022-01-01", "2 years 1 month"),
            ("2020-01", "2021-02-01", "1 year 2 months"),
            ("2020-01-01", "2023-03-01", "3 years 3 months"),
            ("2020-01-01", "2021-01-15", "1 year 1 month"),
            # Months only:
            ("2020-10-10", "2020-11-05", "1 month"),
            ("2020-01-01", "2020-03-15", "3 months"),
            ("2020-05", "2020-05", "1 month"),
            # Months rounding up to years:
            ("2020-01-01", "2021-12-10", "2 years"),
            ("2020-02-01", "2024-01-01", "4 years"),
            # Ongoing, with the current date 2025-06-01:
            ("2021-06-01", "present", "4 years 1 month"),
            ("2021-07-01", None, "4 years"),
        ],
    )
    def test_matches_rendercv_2(
        self,
        typst_value: TypstValue,
        start: int | str,
        end: int | str | None,
        expected: str,
    ) -> None:
        span = typst_value(
            "format-time-span(normalize-date(data.start), normalize-date(data.end),"
            " data.locale, data.current)",
            prelude=prelude,
            data={
                "start": date(start),
                "end": date(end),
                "locale": locale(),
                "current": {"year": 2025, "month": 6, "day": 1},
            },
        )

        assert span == expected

    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            ("2020-01-01", "2021-02-01", "1 año 2 meses"),
            (2020, 2022, "2 años"),
            ("2020-01-01", "2021-01-01", "1 año 1 mes"),
        ],
    )
    def test_uses_the_locale_words(
        self,
        typst_value: TypstValue,
        start: int | str,
        end: int | str,
        expected: str,
    ) -> None:
        span = typst_value(
            "format-time-span(normalize-date(data.start), normalize-date(data.end),"
            " data.locale, data.current)",
            prelude=prelude,
            data={
                "start": date(start),
                "end": date(end),
                "locale": locale(year="año", years="años", month="mes", months="meses"),
                "current": {"year": 2025, "month": 6, "day": 1},
            },
        )

        assert span == expected

    @pytest.mark.parametrize(
        ("start", "end"),
        [
            ({"text": ["Fall 2020"]}, {"year": 2021}),
            ({"year": 2020}, {"text": ["Spring 2021"]}),
            (None, {"year": 2021}),
        ],
    )
    def test_returns_none_for_text_dates(
        self,
        typst_value: TypstValue,
        start: dict[str, Any] | None,
        end: dict[str, Any],
    ) -> None:
        span = typst_value(
            "format-time-span(normalize-date(data.start), normalize-date(data.end),"
            " data.locale, data.current)",
            prelude=prelude,
            data={
                "start": start,
                "end": end,
                "locale": locale(),
                "current": {"year": 2025, "month": 6, "day": 1},
            },
        )

        assert span is None


def test_to_datetime(typst_value: TypstValue) -> None:
    value = typst_value(
        "(to-datetime(normalize-date(data.a), data.current),"
        " to-datetime(normalize-date(data.b), data.current),"
        " to-datetime(normalize-date(data.c), data.current))"
        '.map(it => it.display("[year]-[month]-[day]"))',
        prelude=prelude,
        data={
            "a": {"year": 2020},
            "b": {"year": 2020, "month": 7, "day": 9},
            "c": {"present": True},
            "current": {"year": 2025, "month": 6, "day": 1},
        },
    )

    assert value == ["2020-01-01", "2020-07-09", "2025-06-01"]
