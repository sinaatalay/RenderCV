from typing import Literal, Optional

import pydantic_extra_types.color as pydantic_color

import rendercv.themes.options as o


o.page_show_page_numbering_field_info.default = False


class Page(o.Page):
    show_page_numbering: bool = o.page_show_page_numbering_field_info


o.header_name_bold_field_info.default = False
o.header_alignment_field_info.default = "left"


class Header(o.Header):
    name_bold: bool = o.header_name_bold_field_info
    alignment: o.HeaderAlignment = o.header_alignment_field_info


o.links_use_external_link_icon_field_info.default = False


class Links(o.Links):
    use_external_link_icon: bool = o.links_use_external_link_icon_field_info


o.text_font_family_field_info.default = "Noto Sans"


class Text(o.Text):
    font_family: o.FontFamily = o.text_font_family_field_info


o.section_titles_bold_field_info.default = False


class SectionTitles(o.SectionTitles):
    bold: bool = o.section_titles_bold_field_info


o.highlights_left_margin_field_info.default = "0cm"


class Highlights(o.Highlights):
    left_margin: o.TypstDimension = o.highlights_left_margin_field_info


o.education_entry_first_column_first_row_template_field_info.default = (
    "**INSTITUTION**, AREA -- LOCATION"
)
o.entry_base_with_date_second_column_template_field_info.default = "DATE"


class EducationEntry(o.EducationEntry):
    first_column_first_row_template: str = (
        o.education_entry_first_column_first_row_template_field_info
    )
    second_column_template: str = (
        o.entry_base_with_date_second_column_template_field_info
    )


class NormalEntry(o.NormalEntry):
    second_column_template: str = (
        o.entry_base_with_date_second_column_template_field_info
    )


o.experience_entry_first_column_first_row_template_field_info.default = (
    "**POSITION**, COMPANY -- LOCATION"
)


class ExperienceEntry(o.ExperienceEntry):
    first_column_first_row_template: str = (
        o.experience_entry_first_column_first_row_template_field_info
    )
    second_column_template: str = (
        o.entry_base_with_date_second_column_template_field_info
    )


o.entry_types_education_entry_field_info.default = EducationEntry()
o.entry_types_normal_entry_field_info.default = NormalEntry()
o.entry_types_experience_entry_field_info.default = ExperienceEntry()


class EntryTypes(o.EntryTypes):
    education_entry: EducationEntry = o.entry_types_education_entry_field_info
    normal_entry: NormalEntry = o.entry_types_normal_entry_field_info
    experience_entry: ExperienceEntry = o.entry_types_experience_entry_field_info


o.theme_options_theme_field_info.default = "engineeringresumes"
o.theme_options_page_field_info.default = Page()
o.theme_options_header_field_info.default = Header()
o.theme_options_text_field_info.default = Text()
o.theme_options_entry_types_field_info.default = EntryTypes()
o.theme_options_highlights_field_info.default = Highlights()
o.theme_options_links_field_info.default = Links()
o.theme_options_section_titles_field_info.default = SectionTitles()


class EngineeringclassicThemeOptions(o.ThemeOptions):
    theme: Literal["engineeringclassic"] = o.theme_options_theme_field_info
    page: Page = o.theme_options_page_field_info
    header: Header = o.theme_options_header_field_info
    highlights: Highlights = o.theme_options_highlights_field_info
    text: Text = o.theme_options_text_field_info
    links: Links = o.theme_options_links_field_info
    entry_types: EntryTypes = o.theme_options_entry_types_field_info
    section_titles: SectionTitles = o.theme_options_section_titles_field_info
