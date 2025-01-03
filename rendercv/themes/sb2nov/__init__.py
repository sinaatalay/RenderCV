from typing import Literal, Optional

import pydantic
import pydantic_extra_types.color as pydantic_color

from rendercv.themes.options import (
    BulletPoint,
    Colors,
    EducationEntry,
    EntryTypes,
    ExperienceEntry,
    FontFamily,
    Highlights,
    NormalEntry,
    Text,
    ThemeOptions,
    color_common_description,
    color_common_examples,
    connections_color_description,
    name_color_description,
    section_titles_color_description,
)

sb2nov_second_column_template_field = pydantic.Field(
    default="*LOCATION*\n*DATE*",
    title="Second Column",
    description=(
        "The content of the second column. The available placeholders are"
        " LOCATION and DATE."
    ),
)


class Colors(Colors):
    name: pydantic_color.Color = pydantic.Field(
        default="rgb(0,0,0)",  # type: ignore
        title="Color of Name",
        description=name_color_description,
        examples=color_common_examples,
    )
    connections: pydantic_color.Color = pydantic.Field(
        default="rgb(0,0,0)",  # type: ignore
        title="Color of Connections",
        description=connections_color_description,
        examples=color_common_examples,
    )
    section_titles: pydantic_color.Color = pydantic.Field(
        default="rgb(0,0,0)",  # type: ignore
        title="Color of Section Titles",
        description=section_titles_color_description,
        examples=color_common_examples,
    )


class Text(Text):
    font_family: FontFamily = pydantic.Field(
        default="New Computer Modern",
        title="Font Family",
        description="The font family of the CV.",
    )


class Highlights(Highlights):
    bullet: BulletPoint = pydantic.Field(
        default="◦",
        title="Bullet",
        description="The bullet used for the highlights.",
    )


class EducationEntry(EducationEntry):
    first_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**\n*DEGREE in AREA*",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            " INSTITUTION, AREA, DEGREE, and LOCATION."
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


class NormalEntry(NormalEntry):
    second_column_template: str = sb2nov_second_column_template_field


class ExperienceEntry(ExperienceEntry):
    first_column_first_row_template: str = pydantic.Field(
        default="**POSITION**\n*COMPANY*",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            " COMPANY and POSITION."
        ),
    )

    second_column_template: str = sb2nov_second_column_template_field


class EntryTypes(EntryTypes):
    education_entry: EducationEntry = pydantic.Field(
        default=EducationEntry(),
        title="Education Entry",
        description="Options related to education entries.",
    )
    normal_entry: NormalEntry = pydantic.Field(
        default=NormalEntry(),
        title="Normal Entry",
        description="Options related to normal entries.",
    )
    experience_entry: ExperienceEntry = pydantic.Field(
        default=ExperienceEntry(),
        title="Experience Entry",
        description="Options related to experience entries.",
    )


class Sb2novThemeOptions(ThemeOptions):
    theme: Literal["sb2nov"]
    text: Text = pydantic.Field(
        default=Text(),
        title="Text",
        description="Options related to text.",
    )
    colors: Colors = pydantic.Field(
        default=Colors(),
        title="Colors",
        description="Color used throughout the CV.",
    )
    highlights: Highlights = pydantic.Field(
        default=Highlights(),
        title="Highlights",
        description="Options related to highlights.",
    )
    entry_types: EntryTypes = pydantic.Field(
        default=EntryTypes(),
        title="Entry Types",
        description="Options related to entry types.",
    )
