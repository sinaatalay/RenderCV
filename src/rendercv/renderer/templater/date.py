import calendar
import re
from collections.abc import Sequence
from datetime import date as Date
from typing import Literal

from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.locale.locale import Locale

from .markup import Format, Node, Text, parse_content
from .segments import substitute_placeholders
from .template import compile_template, fill_template, placeholder_names

type Precision = Literal["year", "month", "day"]

time_span_placeholders = frozenset(
    {"HOW_MANY_YEARS", "YEARS", "HOW_MANY_MONTHS", "MONTHS"}
)
date_range_placeholders = frozenset({"START_DATE", "END_DATE"})
# The part of a date that each placeholder of the `single_date` template shows:
date_placeholder_parts: dict[str, Precision] = {
    "MONTH_NAME": "month",
    "MONTH_ABBREVIATION": "month",
    "MONTH": "month",
    "MONTH_IN_TWO_DIGITS": "month",
    "DAY": "day",
    "DAY_IN_TWO_DIGITS": "day",
    "DAY_ORDINAL": "day",
    "YEAR": "year",
    "YEAR_IN_TWO_DIGITS": "year",
}
date_placeholders = frozenset(date_placeholder_parts)
exact_date_pattern = re.compile(r"\d{4}(?:-\d{2}(?:-\d{2})?)?")


def get_precision(date: str | int) -> Precision:
    """Tell which part of a calendar date a date value specifies.

    Why:
        `2020` (or `"2020"`) means a year, `2020-03` a month, and `2020-03-15` (or
        `present`, which is today) a day. Formatting and durations depend on it.

    Args:
        date: A date in YYYY, YYYY-MM, or YYYY-MM-DD format, or "present".

    Returns:
        The precision of the date.
    """
    if date == "present":
        return "day"
    if isinstance(date, int) or len(date) == 4:
        return "year"
    if len(date) == 7:
        return "month"
    return "day"


def build_date_placeholders(date: Date, *, locale: Locale) -> dict[str, str]:
    """Build all date-related template placeholders from a date and locale.

    Why:
        Date placeholders are needed in single_date templates, footer, top_note,
        and file path resolution. Centralizing construction eliminates duplication
        and ensures new placeholders propagate everywhere.

    Args:
        date: Date to extract components from.
        locale: Locale providing month names and abbreviations.

    Returns:
        Dict mapping placeholder names to their string values.
    """
    month = date.month
    day = date.day
    year = date.year

    return {
        "MONTH_NAME": locale.month_names[month - 1],
        "MONTH_ABBREVIATION": locale.month_abbreviations[month - 1],
        "MONTH": str(month),
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "DAY": str(day),
        "DAY_IN_TWO_DIGITS": f"{day:02d}",
        "DAY_ORDINAL": locale.day_ordinals[day - 1],
        "YEAR": str(year),
        "YEAR_IN_TWO_DIGITS": f"{year % 100:02d}",
    }


def date_object_to_string(
    date: Date, *, locale: Locale, single_date_template: str
) -> str:
    """Convert date object to localized string using template placeholders.

    Why:
        Date display varies by locale and user preference. Template-based
        formatting allows MONTH_ABBREVIATION YEAR or MONTH_NAME, YEAR without
        hardcoding formats for each language.

    Example:
        ```py
        result = date_object_to_string(
            Date(2025, 3, 15),
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
        )
        # Returns: "Mar 2025"
        ```

    Args:
        date: Date to format.
        locale: Locale providing month names and abbreviations.
        single_date_template: Template with date placeholders.

    Returns:
        Formatted date string with placeholders substituted.
    """
    return substitute_placeholders(
        single_date_template, build_date_placeholders(date, locale=locale)
    ).strip()


def format_date(
    date: Date,
    *,
    locale: Locale,
    single_date_template: str,
    output_format: Format,
    omitted: frozenset[str] = frozenset(),
) -> tuple[Node, ...]:
    """Format a calendar date with the `single_date` template.

    Why:
        The `single_date` template is a template like the others, so a placeholder
        without a value (an omitted one) is removed together with the separators
        that only existed for it (`MONTH DAY, YEAR` without `YEAR` is `MONTH DAY`).

    Example:
        ```py
        format_date(
            Date(2025, 3, 15),
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION DAY, YEAR",
            output_format="typst",
            omitted=frozenset({"YEAR"}),
        )
        # Returns the content "Mar 15"
        ```

    Args:
        date: Date to format.
        locale: Locale providing month names and abbreviations.
        single_date_template: Template with date placeholders.
        output_format: The output format the template is filled for.
        omitted: Placeholders to leave out.

    Returns:
        The formatted date.
    """
    values = {
        name: (Text(value),)
        for name, value in build_date_placeholders(date, locale=locale).items()
        if name not in omitted
    }
    return fill_template(
        compile_template(single_date_template, date_placeholders),
        values,
        output_format,
    )


def format_single_date(
    date: str | int,
    *,
    locale: Locale,
    single_date_template: str,
    output_format: Format,
) -> tuple[Node, ...]:
    """Format a date value, or pass a custom date text (e.g. "Fall 2023") through.

    Why:
        A year is displayed as the year, `present` as its translation, and a month
        or a day with the `single_date` template. Anything else is custom text.

    Example:
        ```py
        format_single_date(
            "2024-03",
            locale=english_locale,
            single_date_template="MONTH_NAME YEAR",
            output_format="typst",
        )
        # Returns the content "March 2024"
        ```

    Args:
        date: A date in YYYY, YYYY-MM, or YYYY-MM-DD format, "present", or custom
            text.
        locale: Locale providing month names and the translation of "present".
        single_date_template: Template for months and days.
        output_format: The output format the template is filled for.

    Returns:
        The formatted date.
    """
    if date == "present":
        return parse_content(locale.present)
    if isinstance(date, str) and not exact_date_pattern.fullmatch(date):
        # A custom date text (e.g. "Fall 2023"):
        return parse_content(date)
    if get_precision(date) == "year":
        return (Text(str(date)),)
    return format_date(
        get_date_object(date),
        locale=locale,
        single_date_template=single_date_template,
        output_format=output_format,
    )


def find_shared_date_parts(
    start: Date, end: Date, *, locale: Locale, single_date_template: str
) -> tuple[frozenset[str], frozenset[str]]:
    """Find the placeholders that a date range writes once, and where.

    Why:
        The parts of two dates that are coarser than the coarsest part in which
        they differ are the same, like the year of `Mar 2023 to Jun 2023`, so a
        range can write them once. Which date keeps them follows the template, as
        in typography: a part after the parts that differ stays on the end date
        (`Mar to Jun 2023`, `5 to 20 Mar 2023`), a part before them stays on the start
        date (`2023-03 to 06`), and the month and year of `MONTH DAY, YEAR` go to
        both sides (`Mar 5 to 20, 2023`).

    Example:
        ```py
        find_shared_date_parts(
            Date(2023, 3, 1),
            Date(2023, 6, 1),
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
        )
        # Returns: (frozenset({"YEAR"}), frozenset())
        ```

    Args:
        start: Start date.
        end: End date.
        locale: Locale providing month names and abbreviations.
        single_date_template: Template for months and days.

    Returns:
        The placeholders to omit from the start date and from the end date.
    """
    names = placeholder_names(
        compile_template(single_date_template, date_placeholders).nodes
    )
    start_values = build_date_placeholders(start, locale=locale)
    end_values = build_date_placeholders(end, locale=locale)
    coarseness = ("year", "month", "day")
    differing = [
        coarseness.index(date_placeholder_parts[name])
        for name in names
        if start_values[name] != end_values[name]
    ]
    if not differing:
        return frozenset(), frozenset()
    shared = {
        name
        for name in names
        if coarseness.index(date_placeholder_parts[name]) < min(differing)
    }
    kept_positions = [index for index, name in enumerate(names) if name not in shared]

    def positions(name: str) -> list[int]:
        return [index for index, other in enumerate(names) if other == name]

    return (
        frozenset(
            name for name in shared if min(positions(name)) > max(kept_positions)
        ),
        frozenset(
            name for name in shared if max(positions(name)) < min(kept_positions)
        ),
    )


def format_date_range(
    start_date: str | int,
    end_date: str | int,
    *,
    locale: Locale,
    single_date_template: str,
    date_range_template: str,
    shorten: bool,
    output_format: Format,
) -> tuple[Node, ...]:
    """Format a date range with the `date_range` template.

    Why:
        A range whose dates are displayed the same (`Jan 2020 to Jan 2020`) is that
        date. A shortened range writes the parts that its dates share once (see
        `find_shared_date_parts`).

    Example:
        ```py
        format_date_range(
            "2020-06",
            "present",
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE to END_DATE",
            shorten=False,
            output_format="typst",
        )
        # Returns the content "Jun 2020 to present"
        ```

    Args:
        start_date: Start date in YYYY, YYYY-MM, or YYYY-MM-DD format.
        end_date: End date in YYYY, YYYY-MM, or YYYY-MM-DD format, or "present".
        locale: Locale providing month names and the translation of "present".
        single_date_template: Template for months and days.
        date_range_template: Template combining the start and end dates.
        shorten: Whether to write the parts that the dates share once.
        output_format: The output format the templates are filled for.

    Returns:
        The formatted date range.
    """
    start, end = (
        format_single_date(
            date,
            locale=locale,
            single_date_template=single_date_template,
            output_format=output_format,
        )
        for date in (start_date, end_date)
    )
    if start == end:
        return start
    # Only months and days are displayed with `single_date`, so they have parts:
    have_parts = end_date != "present" and "year" not in {
        get_precision(start_date),
        get_precision(end_date),
    }
    if shorten and have_parts:
        omitted = find_shared_date_parts(
            get_date_object(start_date),
            get_date_object(end_date),
            locale=locale,
            single_date_template=single_date_template,
        )
        start, end = (
            format_date(
                get_date_object(date),
                locale=locale,
                single_date_template=single_date_template,
                output_format=output_format,
                omitted=omitted_parts,
            )
            for date, omitted_parts in zip((start_date, end_date), omitted, strict=True)
        )
    return fill_template(
        compile_template(date_range_template, date_range_placeholders),
        {"START_DATE": start, "END_DATE": end},
        output_format,
    )


def get_period(date: str | int, current_date: Date) -> tuple[Date, Date]:
    """Find the first and last days that a date covers.

    Example:
        ```py
        get_period("2020-06", Date(2025, 1, 1))
        # Returns: (Date(2020, 6, 1), Date(2020, 6, 30))
        ```

    Args:
        date: A date in YYYY, YYYY-MM, or YYYY-MM-DD format, or "present".
        current_date: The date that "present" refers to.

    Returns:
        The first and last days.
    """
    first = get_date_object(date, current_date)
    match get_precision(date):
        case "year":
            return first, Date(first.year, 12, 31)
        case "month":
            last_day = calendar.monthrange(first.year, first.month)[1]
            return first, Date(first.year, first.month, last_day)
    return first, first


def sort_entries[T](
    entries: Sequence[T],
    *,
    order: Literal["reverse-chronological", "chronological"],
    current_date: Date,
) -> list[T]:
    """Sort entries by their dates.

    Why:
        An entry is ordered by its end, then its start, so that ongoing and recent
        entries come first in reverse-chronological order. A year or a month covers
        all its days, so `2019 to 2020` ends after `2020-03 to 2020-06`. Entries
        without dates (or with a custom date text) keep their order, after the dated
        ones, and so do entries with the same dates.

    Args:
        entries: Entries of a section.
        order: `"reverse-chronological"` (the most recent first) or `"chronological"`.
        current_date: The date that "present" refers to.

    Returns:
        The sorted entries.
    """

    def get_dates(entry: T) -> tuple[Date, Date] | None:
        start_date = getattr(entry, "start_date", None)
        end_date = getattr(entry, "end_date", None)
        if start_date is not None and end_date is not None:
            return (
                get_period(end_date, current_date)[1],
                get_period(start_date, current_date)[0],
            )
        date = getattr(entry, "date", None)
        if isinstance(date, int) or (
            isinstance(date, str) and exact_date_pattern.fullmatch(date)
        ):
            first, last = get_period(date, current_date)
            return last, first
        return None

    dated = [(dates, entry) for entry in entries if (dates := get_dates(entry))]
    dated.sort(key=lambda item: item[0], reverse=order == "reverse-chronological")
    return [entry for _, entry in dated] + [
        entry for entry in entries if get_dates(entry) is None
    ]


def count_months(start: Date, end: Date) -> int:
    """Count the months needed to cover the days from `start` to `end`, inclusive.

    Why:
        A CV time span answers "how long?" in months, rounding a partial month up,
        so that Feb 2021 to Mar 2021 is 2 months, the same as Mar to Apr. Counting
        calendar months instead of dividing a number of days avoids the drift of
        variable month lengths.

    Example:
        ```py
        count_months(Date(2021, 2, 1), Date(2021, 3, 31))
        # Returns: 2
        ```

    Args:
        start: First day.
        end: Last day (not before `start`).

    Returns:
        The number of months, at least 1.
    """
    months = 12 * (end.year - start.year) + end.month - start.month
    if end.day == calendar.monthrange(end.year, end.month)[1]:
        # The months end with `end`'s month:
        return months + 1
    # A partial month at the end counts as a month:
    return months + (end.day >= start.day)


def compute_time_span(
    start_date: str | int,
    end_date: str | int,
    *,
    locale: Locale,
    current_date: Date,
    time_span_template: str,
    output_format: Format,
) -> tuple[Node, ...]:
    """Compute the duration of a date range and format it, e.g. "2 years 3 months".

    Why:
        A month or day range is measured in months, where a month covers the whole
        month and a day covers the day. A range with a year at either end is
        measured in years (at least one), since its months are unknown. Zero
        components are missing placeholders, so the template drops them with
        their words ("3 months", not "0 years 3 months").

    Example:
        ```py
        compute_time_span(
            "2020-06",
            "2023-09",
            locale=english_locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            output_format="typst",
        )
        # Returns the content "3 years 4 months"
        ```

    Args:
        start_date: Start date in YYYY, YYYY-MM, or YYYY-MM-DD format.
        end_date: End date in YYYY, YYYY-MM, or YYYY-MM-DD format, or "present".
        locale: Locale providing the words for years and months.
        current_date: The date that "present" refers to.
        time_span_template: Template for the duration.
        output_format: The output format the template is filled for.

    Returns:
        The formatted duration.
    """
    start = get_date_object(start_date, current_date)
    end = get_date_object(end_date, current_date)
    precisions = {get_precision(start_date), get_precision(end_date)}
    if "year" in precisions:
        years, months = max(end.year - start.year, 1), 0
    else:
        if get_precision(end_date) == "month":
            # A month covers the whole month:
            end = Date(end.year, end.month, calendar.monthrange(end.year, end.month)[1])
        years, months = divmod(count_months(start, end), 12)

    values: dict[str, str] = {}
    if years:
        values["HOW_MANY_YEARS"] = str(years)
        values["YEARS"] = locale.year if years == 1 else locale.years
    if months:
        values["HOW_MANY_MONTHS"] = str(months)
        values["MONTHS"] = locale.month if months == 1 else locale.months

    template = compile_template(time_span_template, time_span_placeholders)
    return fill_template(
        template,
        {name: parse_content(value) for name, value in values.items()},
        output_format,
    )
