from typing import Literal, Optional

import pydantic

from rendercv.themes.options import (
    ThemeOptions,
    Highlights,
    EntryTypes,
    EducationEntry,
    NormalEntry,
    ExperienceEntry,
)

sb2nov_second_column_template_field = pydantic.Field(
    default="*LOCATION\nDATE*",
    title="Second Column",
    description=(
        "The content of the second column. The available placeholders are"
        " LOCATION and DATE."
    ),
)


class HighlightsSb2nov(Highlights):
    bullet: Literal["•", "●", "◦", "-", "◆", "★", "■", "—", "○"] = pydantic.Field(
        default="◦",
        title="Bullet",
        description="The bullet used for the highlights.",
    )


class EducationEntrySb2nov(EducationEntry):
    first_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**\n*DEGREE in AREA*",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            " INSTITUTION, AREA, and DEGREE."
        ),
    )
    degree_column_template: Optional[str] = pydantic.Field(
        default=None,
        title="Template of the Degree Column",
        description=(
            "If given, a degree column will be added to the education entry. The"
            " available placeholders are DEGREE."
        ),
    )
    second_column_template: str = sb2nov_second_column_template_field


class NormalEntrySb2nov(NormalEntry):
    second_column_template: str = sb2nov_second_column_template_field


class ExperienceEntrySb2nov(ExperienceEntry):
    first_column_first_row_template: str = pydantic.Field(
        default="**POSITION**\n*COMPANY*",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            " COMPANY and POSITION."
        ),
    )

    second_column_template: str = sb2nov_second_column_template_field


class EntryTypesSb2nov(EntryTypes):
    education_entry: EducationEntrySb2nov = pydantic.Field(
        default=EducationEntrySb2nov(),
        title="Education Entry",
        description="Options related to education entries.",
    )
    normal_entry: NormalEntrySb2nov = pydantic.Field(
        default=NormalEntrySb2nov(),
        title="Normal Entry",
        description="Options related to normal entries.",
    )
    experience_entry: ExperienceEntrySb2nov = pydantic.Field(
        default=ExperienceEntrySb2nov(),
        title="Experience Entry",
        description="Options related to experience entries.",
    )


class Sb2novThemeOptions(ThemeOptions):
    theme: Literal["sb2nov"]
