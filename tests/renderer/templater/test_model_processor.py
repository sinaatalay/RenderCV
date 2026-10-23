from datetime import date as Date

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.renderer.templater.model_processor import (
    build_document_placeholders,
    build_name_variants,
    process_model,
)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


@pytest.fixture(params=[["Python", "Remote"], []])
def model(request: pytest.FixtureRequest) -> RenderCVModel:
    """Return a test RenderCVModel with keywords either set or empty.

    Parametrized to test both with and without bold keywords.
    """
    cv_data = {
        # Order matters for connections
        "name": "Jane Doe @",
        "headline": "Software Engineer @",
        "email": "jane@example.com",
        "website": "https://janedoe.dev",
        "sections": {
            "Professional Experience": [
                {
                    "name": "Backend Work",
                    "summary": "Built Python services with *markdown* emphasis.",
                    "highlights": ["Improved Python performance"],
                    "start_date": "2022-01-01",
                    "end_date": "2023-02-01",
                    "location": "Remote",
                }
            ]
        },
    }
    cv = Cv.model_validate(cv_data)

    rendercv_model = RenderCVModel(
        cv=cv, settings=Settings(current_date=Date(2024, 2, 1))
    )
    rendercv_model.settings.bold_keywords = request.param

    return rendercv_model


class TestProcessModel:
    @pytest.mark.parametrize("output_format", ["markdown", "typst"])
    def test_translated_headings_preserve_selectors_and_subsection_titles(
        self, output_format
    ):
        model = RenderCVModel(
            cv={
                "name": "Jane Doe",
                "sections": {
                    "experience": [
                        {
                            "title": "Industry",
                            "entries": [
                                {
                                    "company": "Acme",
                                    "position": "Engineer",
                                    "start_date": "2020-01",
                                    "end_date": "2021-01",
                                }
                            ],
                        }
                    ],
                    "other_work": ["Other work."],
                },
            },
            locale={
                "language": "english",
                "section_labels": {"experience": "**Esperienza**", "Industry": "Wrong"},
            },
        )
        before = model.model_dump()
        result = process_model(model, output_format)
        work, other = result.cv.rendercv_sections
        assert work.key == work.snake_case_title == "experience"
        assert work.title == (
            "**Esperienza**" if output_format == "markdown" else "#strong[Esperienza]"
        )
        assert other.title == "Other Work"
        assert work.entries[0].title == "Industry"
        assert "1 year 1 month" in work.entries[0].entries[0].date_and_location_column
        assert model.model_dump() == before

    @given(label=st.text(alphabet="abc é中文", min_size=1, max_size=20))
    def test_heading_translation_never_changes_section_identity(self, label):
        model = RenderCVModel(
            cv={"name": "Jane Doe", "sections": {"selected_work": ["Work."]}},
            locale={"language": "english", "section_labels": {"selected_work": label}},
        )
        translated = process_model(model, "markdown").cv.rendercv_sections[0]
        assert translated.key == translated.snake_case_title == "selected_work"
        assert model.cv.sections is not None
        assert list(model.cv.sections) == ["selected_work"]

    def test_markdown_output_has_correct_structure(self, model):
        result = process_model(model, "markdown")

        assert result.cv.name == "Jane Doe @"
        assert result.cv.headline == "Software Engineer @"

        # Connections and last updated date are added to cv
        assert result.cv._connections == [
            "[jane@example.com](mailto:jane@example.com)",
            "[janedoe.dev](https://janedoe.dev/)",
        ]
        assert result.cv._top_note == "*Last updated in Feb 2024*"

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column.startswith("**Backend Work**")
        if model.settings.bold_keywords:
            assert (
                "Built **Python** services with *markdown* emphasis."
                in entry.main_column
            )
            assert "- Improved **Python** performance" in entry.main_column
            # DATE placeholder removed because it's not provided; location remains
            assert entry.date_and_location_column == "**Remote**\nJan 2022 – Feb 2023"
        else:
            assert (
                "Built Python services with *markdown* emphasis." in entry.main_column
            )
            assert "- Improved Python performance" in entry.main_column
            assert entry.date_and_location_column == "Remote\nJan 2022 – Feb 2023"

    def test_typst_output_escapes_special_characters(self, model):
        result = process_model(model, "typst")

        assert result.cv.name == "Jane Doe \\@"
        assert result.cv.headline == "Software Engineer \\@"

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column.startswith("#strong[Backend Work]")
        if model.settings.bold_keywords:
            assert "- Improved #strong[Python] performance" in entry.main_column
            assert (
                entry.date_and_location_column == "#strong[Remote]\nJan 2022 – Feb 2023"
            )
            # Connections rendered as Typst links with icons by default
            assert result.cv._connections[0].startswith("#link(")
            assert "#connection-with-icon" in result.cv._connections[0]
        else:
            assert "- Improved Python performance" in entry.main_column
            assert entry.date_and_location_column == "Remote\nJan 2022 – Feb 2023"
            assert result.cv._connections[0].startswith("#link(")
            assert "jane@example.com" in result.cv._connections[0]

    def test_handles_cv_with_no_sections(self):
        cv_data = {
            "name": "Jane Doe",
            "headline": "Software Engineer",
        }
        cv = Cv.model_validate(cv_data)
        rendercv_model = RenderCVModel(cv=cv)

        result = process_model(rendercv_model, "markdown")

        assert result.cv.name == "Jane Doe"
        assert result.cv.headline == "Software Engineer"

    def test_pdf_title_default_placeholder_resolution(self, model):
        result = process_model(model, "typst")

        assert result.settings.pdf_title == "Jane Doe @ - CV"

    def test_pdf_title_is_plain_text(self):
        cv = Cv.model_validate({"name": "**John** Doe"})
        rendercv_model = RenderCVModel(cv=cv)

        result = process_model(rendercv_model, "typst")

        assert result.settings.pdf_title == "John Doe - CV"

    def test_wraps_the_typst_footer_in_a_context(self, model):
        result = process_model(model, "typst")

        assert (
            result.cv._footer == "context { [#emph[Jane Doe \\@ -- #str(here().page())/"
            "#str(counter(page).final().first())]] }"
        )

    def test_does_not_modify_the_model(self, model):
        process_model(model, "typst")

        assert model.cv.name == "Jane Doe @"

    def test_pdf_title_custom_placeholder_resolution(self):
        cv = Cv.model_validate({"name": "John Doe"})
        rendercv_model = RenderCVModel(
            cv=cv, settings=Settings(current_date=Date(2024, 3, 15))
        )
        rendercv_model.settings.pdf_title = "NAME - Resume YEAR"

        result = process_model(rendercv_model, "typst")

        assert result.settings.pdf_title == "John Doe - Resume 2024"

    def test_renders_subsections_like_sections(self):
        cv = Cv.model_validate(
            {
                "name": "Jane Doe",
                "sections": {
                    "experience": [
                        {
                            "title": "*Industry*",
                            "entries": [
                                {
                                    "company": "Acme",
                                    "position": "Engineer",
                                    "start_date": "2020-01",
                                    "end_date": "2021-01",
                                }
                            ],
                        }
                    ]
                },
            }
        )
        rendercv_model = RenderCVModel(
            cv=cv, settings=Settings(current_date=Date(2024, 2, 1))
        )

        result = process_model(rendercv_model, "typst")

        [subsection] = result.cv.rendercv_sections[0].entries
        assert subsection.title == "#emph[Industry]"
        # Its section shows time spans (`experience` does by default):
        assert (
            subsection.entries[0].date_and_location_column
            == "Jan 2020 – Jan 2021\n1 year 1 month"
        )

    def test_sorts_the_entries_of_sections_and_subsections(self):
        entries = [
            {"name": "Old", "date": "2019"},
            {"name": "New", "date": "2023"},
        ]
        cv = Cv.model_validate(
            {
                "name": "Jane Doe",
                "sections": {
                    "projects": entries,
                    "talks": [{"title": "Invited", "entries": entries}],
                },
            }
        )
        rendercv_model = RenderCVModel(
            cv=cv, settings=Settings(sort_entries="reverse-chronological")
        )

        result = process_model(rendercv_model, "markdown")

        projects, talks = result.cv.rendercv_sections
        assert [entry.name for entry in projects.entries] == ["New", "Old"]
        assert [entry.name for entry in talks.entries[0].entries] == ["New", "Old"]


class TestBuildNameVariants:
    def test_none_gives_empty_values(self) -> None:
        result = build_name_variants(None)

        assert len(result) == 7
        assert set(result.values()) == {""}

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_always_7_keys(self, name: str) -> None:
        result = build_name_variants(name)
        assert len(result) == 7

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_snake_case_has_no_spaces(self, name: str) -> None:
        result = build_name_variants(name)
        assert " " not in result["NAME_IN_SNAKE_CASE"]
        assert " " not in result["NAME_IN_LOWER_SNAKE_CASE"]
        assert " " not in result["NAME_IN_UPPER_SNAKE_CASE"]

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_kebab_case_has_no_spaces(self, name: str) -> None:
        result = build_name_variants(name)
        assert " " not in result["NAME_IN_KEBAB_CASE"]
        assert " " not in result["NAME_IN_LOWER_KEBAB_CASE"]
        assert " " not in result["NAME_IN_UPPER_KEBAB_CASE"]

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_lower_variants_are_lowercase(self, name: str) -> None:
        result = build_name_variants(name)
        assert (
            result["NAME_IN_LOWER_SNAKE_CASE"]
            == result["NAME_IN_LOWER_SNAKE_CASE"].lower()
        )
        assert (
            result["NAME_IN_LOWER_KEBAB_CASE"]
            == result["NAME_IN_LOWER_KEBAB_CASE"].lower()
        )

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_upper_variants_are_uppercase(self, name: str) -> None:
        result = build_name_variants(name)
        assert (
            result["NAME_IN_UPPER_SNAKE_CASE"]
            == result["NAME_IN_UPPER_SNAKE_CASE"].upper()
        )
        assert (
            result["NAME_IN_UPPER_KEBAB_CASE"]
            == result["NAME_IN_UPPER_KEBAB_CASE"].upper()
        )

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_original_name_preserved(self, name: str) -> None:
        result = build_name_variants(name)
        assert result["NAME"] == name


def test_build_document_placeholders():
    cv = Cv.model_validate({"name": "John Doe"})
    rendercv_model = RenderCVModel(
        cv=cv, settings=Settings(current_date=Date(2024, 3, 5))
    )

    placeholders = build_document_placeholders(rendercv_model)

    assert placeholders["NAME_IN_SNAKE_CASE"] == "John_Doe"
    assert placeholders["CURRENT_DATE"] == "Mar 2024"
    assert placeholders["DAY_IN_TWO_DIGITS"] == "05"
