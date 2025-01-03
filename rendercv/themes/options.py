"""
The `rendercv.themes.common_options_typst_themes` module contains the standard data
models for the Typst themes' design options. To avoid code duplication, the themes
are encouraged to inherit from these data models.
"""

from typing import Annotated, Literal, Optional

import pydantic
import pydantic_extra_types.color as pydantic_color

from ..data.models.base import RenderCVBaseModelWithoutExtraKeys

# Custom field types:
TypstDimension = Annotated[
    str,
    pydantic.Field(
        pattern=r"\d+\.?\d*(cm|in|pt|mm|ex|em)",
    ),
]


FontFamily = Literal[
    "Libertinus Serif",
    "New Computer Modern",
    "DejaVu Sans Mono",
    "Source Sans 3",
    "Roboto",
    "Open Sans",
    "Ubuntu",
    "Noto Sans",
    "Mukta",
    "Charter",
]

BulletPoint = Literal["•", "◦", "-", "◆", "★", "■", "—", "○"]

PageSize = Literal[
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "a6",
    "a7",
    "a8",
    "us-letter",
    "us-legal",
    "us-executive",
    "us-gov-letter",
    "us-gov-legal",
    "us-business-card",
    "presentation-16-9",
    "presentation-4-3",
]

HeaderAlignment = Literal["left", "center", "right"]
TextAlignment = Literal["left", "justified", "justified-with-no-hyphenation"]

page_size_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default="us-letter",
    title="Page Size",
    description="The page size of the CV.",
)
page_top_margin_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default="2cm",
    title="Top Margin",
    description="The top margin of the page with units (cm, in, pt, mm, ex, em)",
)
page_bottom_margin_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default="2cm",
    title="Bottom Margin",
    description="The bottom margin of the page with units (cm, in, pt, mm, ex, em)",
)
page_left_margin_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default="2cm",
    title="Left Margin",
    description="The left margin of the page with units (cm, in, pt, mm, ex, em)",
)
page_right_margin_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default="2cm",
    title="Right Margin",
    description="The right margin of the page with units (cm, in, pt, mm, ex, em)",
)
page_show_page_numbering_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default=True,
    title="Show Page Numbering",
    description=(
        'If this option is "true", the page numbering will be shown in the footer.'
    ),
)
page_show_last_updated_date_field_info: pydantic.fields.FieldInfo = pydantic.Field(
    default=True,
    title="Show Last Updated Date",
    description=(
        'If this option is "true", the last updated date will be shown in the footer.'
    ),
)


class Page(RenderCVBaseModelWithoutExtraKeys):
    size: PageSize = page_size_field_info
    top_margin: TypstDimension = page_top_margin_field_info
    bottom_margin: TypstDimension = page_bottom_margin_field_info
    left_margin: TypstDimension = page_left_margin_field_info
    right_margin: TypstDimension = page_right_margin_field_info
    show_page_numbering: bool = page_show_page_numbering_field_info
    show_last_updated_date: bool = page_show_last_updated_date_field_info


color_common_description = (
    "\nThe color can be specified either with their name"
    " (https://www.w3.org/TR/SVG11/types.html#ColorKeywords), hexadecimal value, RGB"
    " value, or HSL value."
)
color_common_examples = ["Black", "7fffd4", "rgb(0,79,144)", "hsl(270, 60%, 70%)"]


colors_text_field_info = pydantic.Field(
    default="rgb(0,0,0)",
    title="Color of Text",
    description="The color of the text." + color_common_description,
    examples=color_common_examples,
)
colors_name_field_info = pydantic.Field(
    default="rgb(0,79,144)",
    title="Color of Name",
    description=("The color of the name in the header." + color_common_description),
    examples=color_common_examples,
)
colors_connections_field_info = pydantic.Field(
    default="rgb(0,79,144)",
    title="Color of Connections",
    description=(
        "The color of the connections in the header." + color_common_description
    ),
    examples=color_common_examples,
)
colors_section_titles_field_info = pydantic.Field(
    default="rgb(0,79,144)",
    title="Color of Section Titles",
    description=("The color of the section titles." + color_common_description),
    examples=color_common_examples,
)
colors_links_field_info = pydantic.Field(
    default="rgb(0,79,144)",
    title="Color of Links",
    description="The color of the links." + color_common_description,
    examples=color_common_examples,
)
colors_last_updated_date_and_page_numbering_field_info = pydantic.Field(
    default="rgb(128,128,128)",
    title="Color of Last Updated Date and Page Numbering",
    description=(
        "The color of the last updated date and page numbering."
        + color_common_description
    ),
    examples=color_common_examples,
)


class Colors(RenderCVBaseModelWithoutExtraKeys):
    text: pydantic_color.Color = colors_text_field_info
    name: pydantic_color.Color = colors_name_field_info
    connections: pydantic_color.Color = colors_connections_field_info
    section_titles: pydantic_color.Color = colors_section_titles_field_info
    links: pydantic_color.Color = colors_links_field_info
    last_updated_date_and_page_numbering: pydantic_color.Color = (
        colors_last_updated_date_and_page_numbering_field_info
    )


text_font_family_field_info = pydantic.Field(
    default="Source Sans 3",
    title="Font Family",
    description="The font family.",
)
text_font_size_field_info = pydantic.Field(
    default="10pt",
    title="Font Size",
    description="The font size of the text.",
)
text_leading_field_info = pydantic.Field(
    default="0.6em",
    title="Leading",
    description="The vertical space between adjacent lines of text.",
)
text_alignment_field_info = pydantic.Field(
    default="justified",
    title="Alignment of Text",
    description="The alignment of the text.",
)


class Text(RenderCVBaseModelWithoutExtraKeys):
    font_family: FontFamily = text_font_family_field_info
    font_size: TypstDimension = text_font_size_field_info
    leading: TypstDimension = text_leading_field_info
    alignment: TextAlignment = text_alignment_field_info


links_underline_field_info = pydantic.Field(
    default=False,
    title="Underline Links",
    description='If this option is "true", links will be underlined.',
)
links_use_external_link_icon_field_info = pydantic.Field(
    default=True,
    title="Use External Link Icon",
    description=(
        'If this option is "true", an external link icon will be shown next to the'
        " links."
    ),
)


class Links(RenderCVBaseModelWithoutExtraKeys):
    underline: bool = links_underline_field_info
    use_external_link_icon: bool = links_use_external_link_icon_field_info


header_name_field_info = pydantic.Field(
    default="30pt",
    title="Name Font Size",
    description="The font size of the name in the header.",
)
header_name_bold_field_info = pydantic.Field(
    default=True,
    title="Bold Name",
    description='If this option is "true", the name in the header will be bold.',
)
header_vertical_space_name_connections_field_info = pydantic.Field(
    default="0.7cm",
    title="Vertical Margin Between the Name and Connections",
    description=(
        "The vertical margin between the name of the person and the connections."
    ),
)
header_vertical_space_connections_first_section_field_info = pydantic.Field(
    default="0.7cm",
    title="Vertical Margin Between Connections and First Section",
    description=(
        "The vertical margin between the connections and the first section title."
    ),
)
header_horizontal_space_connections_field_info = pydantic.Field(
    default="0.5cm",
    title="Space Between Connections",
    description="The space between the connections (like phone, email, and website).",
)
header_separator_between_connections_field_info = pydantic.Field(
    default="",
    title="Separator Between Connections",
    description="The separator between the connections in the header.",
)
header_use_icons_for_connections_field_info = pydantic.Field(
    default=True,
    title="Use Icons for Connections",
    description=(
        'If this option is "true", icons will be used for the connections'
        " (phone number, email, social networks, etc.) in the header."
    ),
)
header_alignment_field_info = pydantic.Field(
    default="center",
    title="Alignment of the Header",
    description="The alignment of the header.",
)


class Header(RenderCVBaseModelWithoutExtraKeys):
    name_font_size: TypstDimension = header_name_field_info
    name_bold: bool = header_name_bold_field_info
    vertical_space_between_name_and_connections: TypstDimension = (
        header_vertical_space_name_connections_field_info
    )
    vertical_space_between_connections_and_first_section: TypstDimension = (
        header_vertical_space_connections_first_section_field_info
    )
    horizontal_space_between_connections: TypstDimension = (
        header_horizontal_space_connections_field_info
    )
    separator_between_connections: str = header_separator_between_connections_field_info
    use_icons_for_connections: bool = header_use_icons_for_connections_field_info
    alignment: HeaderAlignment = header_alignment_field_info


section_titles_font_size_field_info = pydantic.Field(
    default="1.4em",
    title="Font Size",
    description="The font size of the section titles.",
)
section_titles_bold_field_info = pydantic.Field(
    default=True,
    title="Bold Section Titles",
    description='If this option is "true", the section titles will be bold.',
)
section_titles_line_type_field_info = pydantic.Field(
    default="partial",
    title="Line Type",
    description="The line type of the section titles.",
)
section_titles_line_thickness_field_info = pydantic.Field(
    default="0.5pt",
    title="Line Thickness",
    description="The thickness of the line under the section titles.",
)
section_titles_vertical_space_above_field_info = pydantic.Field(
    default="0.5cm",
    title="Vertical Space Above Section Titles",
    description="The vertical space above the section titles.",
)
section_titles_vertical_space_below_field_info = pydantic.Field(
    default="0.3cm",
    title="Vertical Space Below Section Titles",
    description="The vertical space below the section titles.",
)


class SectionTitles(RenderCVBaseModelWithoutExtraKeys):
    font_size: TypstDimension = section_titles_font_size_field_info
    bold: bool = section_titles_bold_field_info
    line_type: Literal["partial", "full", "none"] = section_titles_line_type_field_info
    line_thickness: TypstDimension = section_titles_line_thickness_field_info
    vertical_space_above: TypstDimension = (
        section_titles_vertical_space_above_field_info
    )
    vertical_space_below: TypstDimension = (
        section_titles_vertical_space_below_field_info
    )


entries_date_and_location_width_field_info = pydantic.Field(
    default="4.15cm",
    title="Width of Date and Location",
    description="The width of the date and location in the entries.",
)
entries_left_and_right_margin_field_info = pydantic.Field(
    default="0.2cm",
    title="Left and Right Margin",
    description="The left and right margin of the entries.",
)
entries_horizontal_space_between_columns_field_info = pydantic.Field(
    default="0.1cm",
    title="Horizontal Space Between Columns",
    description="The horizontal space between the columns in the entries.",
)
entries_vertical_space_between_entries_field_info = pydantic.Field(
    default="1.2em",
    title="Vertical Space Between Entries",
    description="The vertical space between the entries.",
)
entries_allow_page_break_in_entries_field_info = pydantic.Field(
    default=True,
    title="Allow Page Break in Entries",
    description=(
        'If this option is "true", a page break will be allowed in the entries.'
    ),
)
entries_short_second_row_field_info = pydantic.Field(
    default=False,
    title="Short Second Row",
    description=(
        'If this option is "true", second row will be shortened to leave the bottom'
        " of the date empty."
    ),
)
entries_show_time_spans_in_field_info = pydantic.Field(
    default=[],
    title="Show Time Spans in",
    description=(
        "The list of section titles where the time spans will be shown in the entries."
    ),
)


class Entries(RenderCVBaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = entries_date_and_location_width_field_info
    left_and_right_margin: TypstDimension = entries_left_and_right_margin_field_info
    horizontal_space_between_columns: TypstDimension = (
        entries_horizontal_space_between_columns_field_info
    )
    vertical_space_between_entries: TypstDimension = (
        entries_vertical_space_between_entries_field_info
    )
    allow_page_break_in_entries: bool = entries_allow_page_break_in_entries_field_info
    short_second_row: bool = entries_short_second_row_field_info
    show_time_spans_in: list[str] = entries_show_time_spans_in_field_info


highlights_bullet_field_info = pydantic.Field(
    default="•",
    title="Bullet",
    description="The bullet used for the highlights and bullet entries.",
)
highlights_top_margin_field_info = pydantic.Field(
    default="0.25cm",
    title="Top Margin",
    description="The top margin of the highlights.",
)
highlights_left_margin_field_info = pydantic.Field(
    default="0.4cm",
    title="Left Margin",
    description="The left margin of the highlights.",
)
highlights_vertical_space_between_highlights_field_info = pydantic.Field(
    default="0.25cm",
    title="Vertical Space Between Highlights",
    description="The vertical space between the highlights.",
)
highlights_horizontal_space_between_bullet_and_highlight_field_info = pydantic.Field(
    default="0.5em",
    title="Horizontal Space Between Bullet and Highlight",
    description="The horizontal space between the bullet and the highlight.",
)


class Highlights(RenderCVBaseModelWithoutExtraKeys):
    bullet: BulletPoint = highlights_bullet_field_info
    top_margin: TypstDimension = highlights_top_margin_field_info
    left_margin: TypstDimension = highlights_left_margin_field_info
    vertical_space_between_highlights: TypstDimension = (
        highlights_vertical_space_between_highlights_field_info
    )
    horizontal_space_between_bullet_and_highlight: TypstDimension = (
        highlights_horizontal_space_between_bullet_and_highlight_field_info
    )


entry_base_with_date_first_column_second_row_template_field_info = pydantic.Field(
    default="SUMMARY\nHIGHLIGHTS",
    title="First Column, Second Row",
    description=(
        "The content of the second row of the first column. The available"
        " placeholders are SUMMARY and HIGHLIGHTS."
    ),
)
entry_base_with_date_second_column_template_field_info = pydantic.Field(
    default="LOCATION\nDATE",
    title="Second Column",
    description=(
        "The content of the second column. The available placeholders are LOCATION"
        " and DATE."
    ),
)


class EntryBaseWithDate(RenderCVBaseModelWithoutExtraKeys):
    first_column_second_row_template: str = (
        entry_base_with_date_first_column_second_row_template_field_info
    )
    second_column_template: str = entry_base_with_date_second_column_template_field_info


publication_entry_first_column_first_row_template_field_info = pydantic.Field(
    default="**TITLE**",
    title="First Column",
    description=(
        "The content of the first column. The available placeholders are TITLE,"
        " JOURNAL, and URL."
    ),
)
publication_entry_first_column_second_row_template_field_info = pydantic.Field(
    default="AUTHORS\nURL (JOURNAL)",
    title="First Column, Second Row",
    description=(
        "The content of the second row of the first column. The available placeholders"
        " are AUTHORS, URL, and JOURNAL."
    ),
)
publication_entry_first_column_second_row_without_journal_template_field_info = pydantic.Field(
    default="AUTHORS\nURL",
    title="First Column, Second Row Without Journal",
    description=(
        "The content of the first column in case the journal is not given. The"
        " available placeholders are AUTHORS and URL."
    ),
)
publication_entry_first_column_second_row_without_url_template_field_info = pydantic.Field(
    default="AUTHORS\nJOURNAL",
    title="First Column, Second Row Without URL",
    description=(
        "The content of the first column in case the URL is not given. The"
        " available placeholders are AUTHORS and JOURNAL."
    ),
)


class PublicationEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = (
        publication_entry_first_column_first_row_template_field_info
    )
    first_column_second_row_template: str = (
        publication_entry_first_column_second_row_template_field_info
    )
    first_column_second_row_without_journal_template: str = (
        publication_entry_first_column_second_row_without_journal_template_field_info
    )
    first_column_second_row_without_url_template: str = (
        publication_entry_first_column_second_row_without_url_template_field_info
    )


class PublicationEntry(EntryBaseWithDate, PublicationEntryBase):
    pass


education_entry_first_column_first_row_template_field_info = pydantic.Field(
    default="**INSTITUTION**, AREA",
    title="First Column, First Row",
    description=(
        "The content of the first column. The available placeholders are INSTITUTION,"
        " AREA, DEGREE, and LOCATION."
    ),
)
education_entry_degree_column_template_field_info = pydantic.Field(
    default="**DEGREE**",
    title="Template of the Degree Column",
    description=(
        "If given, a degree column will be added to the education entry. The"
        " available placeholders are DEGREE."
    ),
)
education_entry_degree_column_width_field_info = pydantic.Field(
    default="1cm",
    title="Width of the Degree Column",
    description=(
        'The width of the degree column if the "degree_column_template" is given.'
    ),
)


class EducationEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = (
        education_entry_first_column_first_row_template_field_info
    )
    degree_column_template: Optional[str] = (
        education_entry_degree_column_template_field_info
    )
    degree_column_width: TypstDimension = education_entry_degree_column_width_field_info


class EducationEntry(EntryBaseWithDate, EducationEntryBase):
    pass


normal_entry_first_column_first_row_template_field_info = pydantic.Field(
    default="**NAME**",
    title="First Column, First Row",
    description="The content of the first column. The available placeholders are NAME.",
)


class NormalEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = (
        normal_entry_first_column_first_row_template_field_info
    )


class NormalEntry(EntryBaseWithDate, NormalEntryBase):
    pass


experience_entry_first_column_first_row_template_field_info = pydantic.Field(
    default="**COMPANY**, POSITION",
    title="First Column, First Row",
    description=(
        "The content of the first column. The available placeholders are COMPANY,"
        " POSITION, and LOCATION."
    ),
)


class ExperienceEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = (
        experience_entry_first_column_first_row_template_field_info
    )


class ExperienceEntry(EntryBaseWithDate, ExperienceEntryBase):
    pass


one_line_entry_template_field_info = pydantic.Field(
    default="**LABEL:** DETAILS",
    title="Template",
    description=(
        "The template of the one-line entry. The available placeholders are"
        " LABEL and DETAILS."
    ),
)


class OneLineEntry(RenderCVBaseModelWithoutExtraKeys):
    template: str = one_line_entry_template_field_info


entry_types_one_line_entry_field_info = pydantic.Field(
    default=OneLineEntry(),
    title="One-Line Entry",
    description="Options related to one-line entries.",
)
entry_types_education_entry_field_info = pydantic.Field(
    default=EducationEntry(),
    title="Education Entry",
    description="Options related to education entries.",
)
entry_types_normal_entry_field_info = pydantic.Field(
    default=NormalEntry(),
    title="Normal Entry",
    description="Options related to normal entries.",
)
entry_types_experience_entry_field_info = pydantic.Field(
    default=ExperienceEntry(),
    title="Experience Entry",
    description="Options related to experience entries.",
)
entry_types_publication_entry_field_info = pydantic.Field(
    default=PublicationEntry(),
    title="Publication Entry",
    description="Options related to publication entries.",
)


class EntryTypes(RenderCVBaseModelWithoutExtraKeys):
    one_line_entry: OneLineEntry = entry_types_one_line_entry_field_info
    education_entry: EducationEntry = entry_types_education_entry_field_info
    normal_entry: NormalEntry = entry_types_normal_entry_field_info
    experience_entry: ExperienceEntry = entry_types_experience_entry_field_info
    publication_entry: PublicationEntry = entry_types_publication_entry_field_info


theme_options_theme_field_info = pydantic.Field(
    default="tobeoverwritten",
    title="Theme",
    description="The theme of the CV. It just changes the default values.",
)
theme_options_page_field_info = pydantic.Field(
    default=Page(),
    title="Page",
    description="Options related to the page.",
)
theme_options_colors_field_info = pydantic.Field(
    default=Colors(),
    title="Colors",
    description="Color used throughout the CV.",
)
theme_options_text_field_info = pydantic.Field(
    default=Text(),
    title="Text",
    description="Options related to text.",
)
theme_options_links_field_info = pydantic.Field(
    default=Links(),
    title="Links",
    description="Options related to links.",
)
theme_options_header_field_info = pydantic.Field(
    default=Header(),
    title="Headers",
    description="Options related to headers.",
)
theme_options_section_titles_field_info = pydantic.Field(
    default=SectionTitles(),
    title="Section Titles",
    description="Options related to section titles.",
)
theme_options_entries_field_info = pydantic.Field(
    default=Entries(),
    title="Entries",
    description="Options related to entries.",
)
theme_options_highlights_field_info = pydantic.Field(
    default=Highlights(),
    title="Highlights",
    description="Options related to highlights.",
)
theme_options_entry_types_field_info = pydantic.Field(
    default=EntryTypes(),
    title="Templates",
    description="Options related to the templates.",
)


class ThemeOptions(RenderCVBaseModelWithoutExtraKeys):
    theme: Literal["tobeoverwritten"] = theme_options_theme_field_info
    page: Page = theme_options_page_field_info
    colors: Colors = theme_options_colors_field_info
    text: Text = theme_options_text_field_info
    links: Links = theme_options_links_field_info
    header: Header = theme_options_header_field_info
    section_titles: SectionTitles = theme_options_section_titles_field_info
    entries: Entries = theme_options_entries_field_info
    highlights: Highlights = theme_options_highlights_field_info
    entry_types: EntryTypes = theme_options_entry_types_field_info
