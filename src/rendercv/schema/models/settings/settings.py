from datetime import date as Date
from typing import Annotated, Literal

import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..custom_error_types import invalid_input
from .render_command import RenderCommand

type PdfStandard = Literal[
    "1.4",
    "1.5",
    "1.6",
    "1.7",
    "2.0",
    "a-1a",
    "a-1b",
    "a-2a",
    "a-2b",
    "a-2u",
    "a-3a",
    "a-3b",
    "a-3u",
    "a-4",
    "a-4e",
    "a-4f",
    "ua-1",
]


class Settings(BaseModelWithoutExtraKeys):
    current_date: Annotated[
        Date | Literal["today"],
        invalid_input(
            "rendercv_current_date",
            "This is not a valid `current_date`. Please use YYYY-MM-DD format or"
            ' "today".',
        ),
    ] = pydantic.Field(
        default="today",
        title="Date",
        description=(
            'The date to use as "current date" for filenames, the "last updated" label,'
            " and time span calculations. Defaults to the actual current date."
        ),
    )
    render_command: RenderCommand = pydantic.Field(
        default_factory=RenderCommand,
        title="Render Command Settings",
        description=(
            "Settings for the `render` command. These correspond to command-line"
            " arguments. CLI arguments take precedence over these settings."
        ),
    )
    bold_keywords: list[str] = pydantic.Field(
        default=[],
        title="Bold Keywords",
        description="Keywords to automatically bold in the output.",
    )
    sort_entries: Literal["none", "reverse-chronological", "chronological"] = (
        pydantic.Field(
            default="none",
            title="Sort Entries",
            description=(
                "The order of the entries of every section and subsection: as written"
                " (`none`), the most recent first (`reverse-chronological`), or the"
                " oldest first (`chronological`). Entries are ordered by their end"
                " dates, then their start dates, and the ones without dates come last"
                " in their written order. The default value is `none`."
            ),
        )
    )
    pdf_title: str = pydantic.Field(
        default="NAME - CV",
        title="PDF Title",
        description=(
            "Title metadata for the PDF document. This appears in browser tabs and PDF"
            " readers. Available placeholders:\n- `NAME`: The CV owner's name from"
            " `cv.name`\n- `CURRENT_DATE`: Formatted date based on"
            " `design.templates.single_date`\n- `MONTH_NAME`: Full month name (e.g.,"
            " January)\n- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n-"
            " `MONTH`: Month number (e.g., 1)\n- `MONTH_IN_TWO_DIGITS`: Zero-padded"
            " month (e.g., 01)\n- `DAY`: Day of the month (e.g., 5)\n-"
            " `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n- `DAY_ORDINAL`: Day as"
            " an ordinal (e.g., 5th), from `locale.day_ordinals`\n- `YEAR`: Full year"
            " (e.g., 2025)\n- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\nThe"
            " default value is `NAME - CV`."
        ),
    )
    pdf_standards: list[PdfStandard] = pydantic.Field(
        default=["ua-1"],
        title="PDF Standards",
        description=(
            "Standards that the PDF conforms to. PDF/UA-1 (`ua-1`) is the accessibility"
            " standard: screen readers and parsers read the PDF in its logical order,"
            " with every image and formula described. It requires a name (the CV's"
            " main heading). RenderCV describes its own images and formulas; those in"
            ' your own Typst code need alternative text (`#image("logo.png", alt:'
            ' "Logo")`). PDF/A (`a-2b`, ...) is the archival standard. The default'
            " value is `['ua-1']`."
        ),
    )
    _resolved_current_date: Date = pydantic.PrivateAttr()

    @pydantic.field_validator("pdf_standards")
    @classmethod
    def validate_pdf_standards(cls, standards: list[PdfStandard]) -> list[PdfStandard]:
        """Require compatible PDF versions, archival, and accessibility standards.

        Args:
            standards: The requested standards.

        Returns:
            The compatible standards, unchanged.

        Raises:
            ValueError: Multiple standards of one kind or incompatible versions.
        """
        # Typst's PDF standards share a version range; see its PDF reference.
        versions = {"1.4", "1.5", "1.6", "1.7", "2.0"}
        kinds: set[str] = set()
        for standard in standards:
            kind = standard.split("-")[0] if "-" in standard else "version"
            if kind in kinds:
                raise ValueError(
                    "Choose at most one PDF version, one PDF/A standard, and one"
                    " PDF/UA standard."
                )
            kinds.add(kind)
            if standard.startswith("a-1"):
                versions &= {"1.4"}
            elif standard.startswith("a-4"):
                versions &= {"2.0"}
            elif kind in {"a", "ua"}:
                versions.discard("2.0")
            else:
                versions &= {standard}
        if not versions:
            message = f"These PDF standards are incompatible: {', '.join(standards)}."
            raise ValueError(message)
        return standards

    @pydantic.field_validator("bold_keywords")
    @classmethod
    def keep_unique_keywords(cls, value: list[str]) -> list[str]:
        """Remove duplicate keywords from bold list.

        Why:
            Users might accidentally list same keyword multiple times. Deduplication
            prevents redundant bold highlighting operations during rendering.

        Args:
            value: List of keywords potentially with duplicates.

        Returns:
            List with unique keywords only.
        """
        return list(dict.fromkeys(value))

    @pydantic.model_validator(mode="after")
    def resolve_current_date(self) -> "Settings":
        self._resolved_current_date = (
            Date.today() if self.current_date == "today" else self.current_date
        )
        return self
