from collections.abc import Mapping
from typing import Any

import pydantic
import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.schema.models.custom_error_types import CustomPydanticErrorTypes
from rendercv.schema.models.cv.entry_types import (
    Entry,
    EntryTypeDeclaration,
)
from rendercv.schema.models.cv.section import (
    Section,
    Sections,
    dictionary_key_to_proper_section_title,
    section_key,
)
from rendercv.schema.models.validation_context import ValidationContext

sections_adapter = pydantic.TypeAdapter[list[Section]](Sections)


@pytest.fixture
def validation_context(
    standard_entry_types: Mapping[str, EntryTypeDeclaration],
    standard_entry_type_models: Mapping[str, type[pydantic.BaseModel]],
) -> dict[str, ValidationContext]:
    return {
        "context": ValidationContext(
            entry_types=standard_entry_types,
            entry_type_models=standard_entry_type_models,
        )
    }


class TestDictionaryKeyToProperSectionTitle:
    @pytest.mark.parametrize(
        ("key", "expected_section_title"),
        [
            ("education", "Education"),
            ("this_is_a_test", "This Is a Test"),
            ("education_and_training", "Education and Training"),
            ("welcome_to_rendercv!", "Welcome to Rendercv!"),
            ("Welcome to RenderCV!", "Welcome to RenderCV!"),
            ("Hello_World", "Hello_World"),
            ("Hello World", "Hello World"),
            ("2024", "2024"),
        ],
    )
    def test_converts_snake_case_keys_to_titles(
        self, key: str, expected_section_title: str
    ) -> None:
        assert dictionary_key_to_proper_section_title(key) == expected_section_title

    @given(key=st.from_regex(r"[a-z]{1,5}(_[a-z]{1,5}){0,3}", fullmatch=True))
    def test_snake_case_replaces_underscores_with_spaces(self, key: str) -> None:
        result = dictionary_key_to_proper_section_title(key)

        assert "_" not in result
        assert result.lower() == key.replace("_", " ")

    @given(
        parts=st.lists(
            st.from_regex(r"[a-zA-Z0-9]{1,10}", fullmatch=True),
            min_size=2,
            max_size=5,
        )
    )
    def test_keys_with_spaces_are_kept(self, parts: list[str]) -> None:
        key = " ".join(parts)

        assert dictionary_key_to_proper_section_title(key) == key

    @given(key=st.from_regex(r"[a-z_]*[A-Z][a-zA-Z_]*", fullmatch=True))
    def test_keys_with_uppercase_letters_are_kept(self, key: str) -> None:
        assert dictionary_key_to_proper_section_title(key) == key


@pytest.mark.parametrize(
    ("title", "expected_key"),
    [
        ("Experience", "experience"),
        ("Education and Training", "education_and_training"),
        ("Welcome to RenderCV!", "welcome_to_rendercv!"),
        ("2024", "2024"),
    ],
)
def test_section_key(title: str, expected_key: str) -> None:
    assert section_key(title) == expected_key


def test_section() -> None:
    section = Section(title="Experience", key="experience")

    assert section.entries == ()
    assert section.subsections == ()


class TestValidateSections:
    def test_validates_sections_in_order(
        self, validation_context: dict[str, ValidationContext]
    ) -> None:
        sections = sections_adapter.validate_python(
            {
                "summary": ["I build things."],
                "technical_skills": [{"label": "Languages", "details": "Python"}],
                "Selected Projects": [{"name": "RenderCV"}, {"name": "Typst"}],
            },
            context=validation_context,
        )

        assert [(section.title, section.key) for section in sections] == [
            ("Summary", "summary"),
            ("Technical Skills", "technical_skills"),
            ("Selected Projects", "selected_projects"),
        ]
        assert sections[0].entries == (
            Entry(type_name="paragraph", values={"text": "I build things."}),
        )
        assert [entry.type_name for entry in sections[2].entries] == [
            "normal",
            "normal",
        ]

    def test_allows_different_entry_types_in_one_section(
        self, validation_context: dict[str, ValidationContext]
    ) -> None:
        sections = sections_adapter.validate_python(
            {
                "mixed": [
                    "Some text.",
                    {"bullet": "A point."},
                    {"company": "ACME", "position": "Engineer"},
                ]
            },
            context=validation_context,
        )

        assert [entry.type_name for entry in sections[0].entries] == [
            "paragraph",
            "bullet",
            "experience",
        ]

    def test_validates_subsections(
        self, validation_context: dict[str, ValidationContext]
    ) -> None:
        sections = sections_adapter.validate_python(
            {
                "publications": {
                    "journal_articles": [{"title": "Paper", "authors": ["A"]}],
                    2024: [{"title": "Other", "authors": ["B"]}],
                    "Talks": None,
                }
            },
            context=validation_context,
        )

        (publications,) = sections
        assert publications.title == "Publications"
        assert publications.entries == ()
        assert [
            (subsection.title, subsection.key, len(subsection.entries))
            for subsection in publications.subsections
        ] == [
            ("Journal Articles", "journal_articles", 1),
            ("2024", "2024", 1),
            ("Talks", "talks", 0),
        ]
        assert publications.subsections[0].subsections == ()

    @pytest.mark.parametrize("value", [None, []])
    def test_empty_sections_have_no_entries(
        self, validation_context: dict[str, ValidationContext], value: Any
    ) -> None:
        sections = sections_adapter.validate_python(
            {"references": value}, context=validation_context
        )

        assert sections == [Section(title="References", key="references")]

    @pytest.mark.parametrize("value", [["a"], "text", 5, None])
    def test_rejects_sections_that_are_not_mappings(
        self, validation_context: dict[str, ValidationContext], value: Any
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            sections_adapter.validate_python(value, context=validation_context)

        error = exc_info.value.errors()[0]
        assert error["type"] == CustomPydanticErrorTypes.other.value
        assert error["msg"] == (
            "Sections should be a mapping of section titles to lists of entries."
        )

    def test_collects_every_problem_with_its_location(
        self, validation_context: dict[str, ValidationContext]
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            sections_adapter.validate_python(
                {
                    "experience": [
                        {"company": "ACME", "position": "Engineer"},
                        {"company": "ACME", "positon": "Engineer"},
                    ],
                    "education": {
                        "degrees": [{"institution": "MIT", "area": "CS"}, None],
                        "courses": "not a list",
                    },
                    "skills": "not a list",
                    "projects": [{"name": "X", "start_date": "bad"}],
                },
                context=validation_context,
            )

        (error,) = exc_info.value.errors()
        assert error["type"] == CustomPydanticErrorTypes.entry_validation.value
        assert error["msg"] == "There are problems with the entries."
        caused_by = error["ctx"]["caused_by"]
        assert [(cause["loc"], cause["msg"]) for cause in caused_by] == [
            (
                ("experience", 1, "positon"),
                "The entry type `experience` has no field `positon`. Did you mean"
                " `position`?",
            ),
            (
                ("education", "degrees", 1),
                "An entry should be a mapping of fields or text.",
            ),
            (
                ("education", "courses"),
                "A section should be a list of entries, or a mapping of subsection"
                " titles to lists of entries.",
            ),
            (
                ("skills",),
                "A section should be a list of entries, or a mapping of subsection"
                " titles to lists of entries.",
            ),
            (
                ("projects", 0, "start_date"),
                'This is not a valid date. Use YYYY-MM-DD, YYYY-MM, YYYY, or "present".',
            ),
        ]

    def test_without_entry_types_no_entry_is_valid(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            sections_adapter.validate_python({"projects": [{"name": "X"}]})

        (cause,) = exc_info.value.errors()[0]["ctx"]["caused_by"]
        assert cause["loc"] == ("projects", 0)
        assert "There are no entry types" in cause["msg"]

    def test_json_schema_describes_sections(self) -> None:
        schema = sections_adapter.json_schema()

        assert schema["type"] == "object"
        assert schema["additionalProperties"]["anyOf"] == [
            {"type": "array"},
            {"type": "object", "additionalProperties": {"type": "array"}},
        ]
