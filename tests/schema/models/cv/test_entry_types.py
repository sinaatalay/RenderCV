from collections.abc import Mapping
from datetime import date as Date
from typing import Any

import pydantic
import pydantic_core
import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.cv.entry_types import (
    Bullet,
    DateValue,
    Entry,
    EntryTypeDeclaration,
    FieldDeclaration,
    PhoneValue,
    available_field_kinds,
    build_entry_type_models,
    check_date_order,
    closest_entry_type,
    date_pattern,
    detect_entry_type,
    entry_type_key,
    error_details,
    parse_entry_type_declarations,
    split_bullet,
    validate_date,
    validate_email,
    validate_entry,
    validate_list,
    validate_markdown,
    validate_phone,
    validate_url,
)
from rendercv.schema.yaml_reader import TypstString

type EntryTypes = Mapping[str, EntryTypeDeclaration]
type EntryTypeModels = Mapping[str, type[pydantic.BaseModel]]


def make_entry_types(
    declarations: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, EntryTypeDeclaration]:
    return parse_entry_type_declarations(
        {
            name: {"doc": f"The {name} type.", "fields": fields}
            for name, fields in declarations.items()
        }
    )


# One entry type with a field of every kind, and a small type to nest in it:
every_kind_entry_types = make_entry_types(
    {
        "every_kind": {
            "title": {"kind": "markdown", "doc": "The title."},
            "code": {"kind": "text", "optional": True, "pattern": "[A-Z]{3}"},
            "label": {"kind": "text", "optional": True},
            "when": {"kind": "date", "optional": True},
            "season": {"kind": "date", "optional": True, "allow-text": True},
            "link": {"kind": "url", "optional": True},
            "mail": {"kind": "email", "optional": True},
            "phone": {"kind": "phone", "optional": True},
            "amount": {"kind": "number", "optional": True},
            "visible": {"kind": "bool", "optional": True},
            "level": {"kind": "choice", "optional": True, "choices": ["low", "high"]},
            "tags": {"kind": "list", "optional": True},
            "dates": {"kind": "list", "optional": True, "of": "date"},
            "levels": {
                "kind": "list",
                "optional": True,
                "of": "choice",
                "choices": ["low", "high"],
            },
            "points": {"kind": "bullets", "optional": True},
            "children": {"kind": "entries", "optional": True},
        },
        "child": {"name": {"kind": "markdown"}},
    }
)
every_kind_models = build_entry_type_models(every_kind_entry_types)

# Two types with the same fields, so entries fit both:
twin_entry_types = make_entry_types(
    {
        "talk": {"title": {"kind": "markdown"}, "date": {"kind": "date"}},
        "award": {"title": {"kind": "markdown"}, "date": {"kind": "date"}},
    }
)
twin_models = build_entry_type_models(twin_entry_types)


def validate_every_kind(
    **values: Any,
) -> tuple[Entry | None, list[pydantic_core.ErrorDetails]]:
    return validate_entry(
        {"title": "Title", **values}, every_kind_entry_types, every_kind_models
    )


class TestParseEntryTypeDeclarations:
    def test_fills_in_defaults(self) -> None:
        entry_types = make_entry_types({"note": {"body": {"kind": "markdown"}}})

        assert entry_types["note"] == EntryTypeDeclaration(
            name="note",
            doc="The note type.",
            fields={"body": FieldDeclaration(kind="markdown")},
        )

    def test_reads_every_field_option(self) -> None:
        entry_types = make_entry_types(
            {
                "rating": {
                    "levels": {
                        "kind": "list",
                        "optional": True,
                        "doc": "The levels.",
                        "of": "choice",
                        "choices": ["low", "high"],
                        "pattern": "x",
                        "allow-text": True,
                    }
                }
            }
        )

        assert entry_types["rating"].fields["levels"] == FieldDeclaration(
            kind="list",
            optional=True,
            doc="The levels.",
            of="choice",
            choices=("low", "high"),
            pattern="x",
            allow_text=True,
        )

    def test_reads_typst_nones_as_unset(self) -> None:
        # Typst's `declarations` reports unset options as JSON null:
        entry_types = parse_entry_type_declarations(
            {
                "note": {
                    "doc": None,
                    "fields": {
                        "body": {
                            "kind": "markdown",
                            "optional": False,
                            "doc": None,
                            "of": None,
                            "choices": None,
                            "pattern": None,
                            "allow-text": False,
                        }
                    },
                }
            }
        )

        assert entry_types["note"].doc is None
        assert entry_types["note"].fields["body"] == FieldDeclaration(kind="markdown")

    def test_keeps_declaration_order(self) -> None:
        entry_types = make_entry_types(
            {
                "zebra": {"b": {"kind": "markdown"}, "a": {"kind": "markdown"}},
                "apple": {"c": {"kind": "markdown"}},
            }
        )

        assert list(entry_types) == ["zebra", "apple"]
        assert list(entry_types["zebra"].fields) == ["b", "a"]

    def test_rejects_the_reserved_type_field(self) -> None:
        with pytest.raises(
            RenderCVUserError, match="`type`, but that name is reserved"
        ):
            make_entry_types({"note": {entry_type_key: {"kind": "markdown"}}})

    @pytest.mark.parametrize(
        "field",
        [{"kind": "paragraph"}, {"kind": "list", "of": "paragraph"}],
    )
    def test_rejects_unknown_kinds(self, field: dict[str, Any]) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"The field `body` of the entry type `note` has the unknown kind"
            r" `paragraph`\. Available kinds: markdown, text,",
        ):
            make_entry_types({"note": {"body": field}})

    def test_reads_the_standard_entry_types(
        self, standard_entry_types: EntryTypes
    ) -> None:
        assert list(standard_entry_types) == [
            "normal",
            "experience",
            "education",
            "publication",
            "one_line",
            "bullet",
            "numbered",
            "reversed_numbered",
            "paragraph",
        ]
        assert standard_entry_types["publication"].fields["authors"] == (
            FieldDeclaration(
                kind="list",
                of="markdown",
                doc=standard_entry_types["publication"].fields["authors"].doc,
            )
        )
        assert standard_entry_types["normal"].fields["date"].allow_text
        assert not standard_entry_types["normal"].fields["start_date"].allow_text


def test_available_field_kinds() -> None:
    assert available_field_kinds == (
        "markdown",
        "text",
        "date",
        "url",
        "email",
        "phone",
        "number",
        "bool",
        "choice",
        "list",
        "bullets",
        "entries",
    )


@pytest.mark.parametrize(
    ("entry_type_name", "expected_required_fields"),
    [
        ("normal", {"name"}),
        ("experience", {"company", "position"}),
        ("education", {"institution", "area"}),
        ("publication", {"title", "authors"}),
        ("one_line", {"label", "details"}),
        ("bullet", {"bullet"}),
        ("numbered", {"number"}),
        ("reversed_numbered", {"reversed_number"}),
        ("paragraph", {"text"}),
    ],
)
def test_entry_type_declaration(
    standard_entry_types: EntryTypes,
    entry_type_name: str,
    expected_required_fields: set[str],
) -> None:
    entry_type = standard_entry_types[entry_type_name]

    assert entry_type.name == entry_type_name
    assert entry_type.doc
    assert entry_type.required_fields == expected_required_fields


class TestDateValue:
    @pytest.mark.parametrize(
        ("date_value", "expected_date"),
        [
            (DateValue(year=2020), Date(2020, 1, 1)),
            (DateValue(year=2020, month=5), Date(2020, 5, 1)),
            (DateValue(year=2020, month=5, day=17), Date(2020, 5, 17)),
            (DateValue(present=True), Date(2024, 6, 15)),
            (DateValue(text="Fall 2023"), None),
        ],
    )
    def test_to_date(self, date_value: DateValue, expected_date: Date | None) -> None:
        assert date_value.to_date(Date(2024, 6, 15)) == expected_date


class TestValidateDate:
    @pytest.mark.parametrize(
        ("value", "expected_date_value"),
        [
            ("2020", DateValue(year=2020)),
            (2020, DateValue(year=2020)),
            (1, DateValue(year=1)),
            (9999, DateValue(year=9999)),
            ("2020-05", DateValue(year=2020, month=5)),
            ("2020-05-17", DateValue(year=2020, month=5, day=17)),
            (" 2020-05 ", DateValue(year=2020, month=5)),
            ("2024-02-29", DateValue(year=2024, month=2, day=29)),
            (Date(2020, 5, 17), DateValue(year=2020, month=5, day=17)),
            ("present", DateValue(present=True)),
            (" present ", DateValue(present=True)),
        ],
    )
    @pytest.mark.parametrize("allow_text", [False, True])
    def test_accepts_dates(
        self, value: Any, expected_date_value: DateValue, allow_text: bool
    ) -> None:
        assert validate_date(value, allow_text=allow_text) == expected_date_value

    @pytest.mark.parametrize(
        "value",
        [
            "Fall 2023",
            "Present",
            "2020-1",
            "20201",
            "2020-05-05T10:00",
            "",
            "   ",
            0,
            -5,
            10000,
            2020.5,
            True,
            None,
            [2020],
        ],
    )
    def test_rejects_non_dates(self, value: Any) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError) as exc_info:
            validate_date(value, allow_text=False)

        assert exc_info.value.type == "rendercv_date"
        assert exc_info.value.message() == (
            'This is not a valid date. Use YYYY-MM-DD, YYYY-MM, YYYY, or "present".'
        )

    # Python's wording of the reason differs between versions, so only the part
    # it names is checked:
    @pytest.mark.parametrize(
        ("value", "expected_reason"),
        [
            ("2020-13", "month"),
            ("2020-00", "month"),
            ("2020-05-00", "day"),
            ("2020-02-30", "day"),
            ("2023-02-29", "day"),
            ("0000", "year"),
        ],
    )
    @pytest.mark.parametrize("allow_text", [False, True])
    def test_rejects_impossible_dates_with_the_reason(
        self, value: str, expected_reason: str, allow_text: bool
    ) -> None:
        # Text shaped like a date is never taken as free text:
        with pytest.raises(pydantic_core.PydanticCustomError) as exc_info:
            validate_date(value, allow_text=allow_text)

        assert exc_info.value.message().startswith("This is not a valid date: ")
        assert expected_reason in exc_info.value.message()

    @pytest.mark.parametrize("value", ["Fall 2023", "Present", "2020-1", "Since 2019"])
    def test_accepts_free_text_when_allowed(self, value: str) -> None:
        assert validate_date(value, allow_text=True) == DateValue(text=value)

    @pytest.mark.parametrize("value", ["", "   ", 0, 2020.5, True, None])
    def test_rejects_non_dates_when_text_is_allowed(self, value: Any) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError) as exc_info:
            validate_date(value, allow_text=True)

        assert exc_info.value.message().endswith(
            "\"present\", or any text like 'Fall 2023'."
        )

    @given(date=st.dates())
    def test_iso_dates_round_trip(self, date: Date) -> None:
        date_value = validate_date(date.isoformat(), allow_text=False)

        assert date_value == DateValue(year=date.year, month=date.month, day=date.day)
        assert date_value.to_date(Date.today()) == date

    @given(year=st.integers(1, 9999), month=st.integers(1, 12))
    def test_year_and_month_dates_round_trip(self, year: int, month: int) -> None:
        date_value = validate_date(f"{year:04d}-{month:02d}", allow_text=False)

        assert date_value == DateValue(year=year, month=month)
        assert date_value.to_date(Date.today()) == Date(year, month, 1)

    @given(
        text=st.text(min_size=1).filter(
            lambda text: (
                bool(text.strip())
                and text.strip() != "present"
                and date_pattern.fullmatch(text.strip()) is None
            )
        )
    )
    def test_keeps_any_other_text_as_it_is(self, text: str) -> None:
        assert validate_date(text, allow_text=True) == DateValue(text=text)


class TestValidateMarkdown:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("**Bold** text", "**Bold** text"),
            (2024, "2024"),
            (3.5, "3.5"),
            ("", ""),
        ],
    )
    def test_accepts_text_and_numbers(self, value: Any, expected: str) -> None:
        assert validate_markdown(value) == expected

    def test_keeps_typst_strings(self) -> None:
        value = TypstString("$x^2$")

        result = validate_markdown(value)

        assert isinstance(result, TypstString)
        assert result == "$x^2$"

    @pytest.mark.parametrize("value", [True, None, ["a"], {"a": "b"}])
    def test_rejects_other_values(self, value: Any) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError, match="should be text"):
            validate_markdown(value)


class TestSplitBullet:
    @pytest.mark.parametrize(
        ("text", "expected_bullet"),
        [
            ("Built a compiler", Bullet(body="Built a compiler")),
            (
                "Published papers - ICML 2022 - NeurIPS 2022",
                Bullet(
                    body="Published papers",
                    children=(Bullet(body="ICML 2022"), Bullet(body="NeurIPS 2022")),
                ),
            ),
            ("A well-known tool", Bullet(body="A well-known tool")),
            ("Ranges like 2020-2021", Bullet(body="Ranges like 2020-2021")),
            ("Negative -5 values", Bullet(body="Negative -5 values")),
            ("Dash at the end -", Bullet(body="Dash at the end -")),
            ("", Bullet(body="")),
        ],
    )
    def test_splits_nested_bullets_on_spaced_dashes(
        self, text: str, expected_bullet: Bullet
    ) -> None:
        assert split_bullet(text) == expected_bullet

    def test_does_not_split_typst_strings(self) -> None:
        bullet = split_bullet(TypstString("$a - b$ - c"))

        assert bullet == Bullet(body="$a - b$ - c")
        assert isinstance(bullet.body, TypstString)

    @given(
        parts=st.lists(
            st.text(alphabet=st.characters(blacklist_characters="-")),
            min_size=1,
            max_size=6,
        )
    )
    def test_joined_parts_split_back(self, parts: list[str]) -> None:
        bullet = split_bullet(" - ".join(parts))

        assert bullet.body == parts[0]
        assert [child.body for child in bullet.children] == parts[1:]
        assert all(child.children == () for child in bullet.children)


class TestValidatePhone:
    def test_writes_the_number_in_every_format(self) -> None:
        assert validate_phone("+1 415 555 0100") == PhoneValue(
            e164="+14155550100",
            international="+1 415-555-0100",
            national="(415) 555-0100",
            uri="tel:+1-415-555-0100",
        )

    @pytest.mark.parametrize(
        "value", ["+14155550100", "+1-415-555-0100", "+1 (415) 555-0100"]
    )
    def test_accepts_any_international_notation(self, value: str) -> None:
        assert validate_phone(value).e164 == "+14155550100"

    @pytest.mark.parametrize("value", ["not a phone", "4155550100", 14155550100, ""])
    def test_rejects_invalid_numbers(self, value: Any) -> None:
        with pytest.raises(ValueError, match="not a valid phone number"):
            validate_phone(value)


class TestValidateUrl:
    @pytest.mark.parametrize(
        "value",
        [
            "https://example.com",
            "https://example.com/",
            "http://example.com/a/b?c=d#e",
            "https://EXAMPLE.com/Path",
        ],
    )
    def test_returns_the_url_as_written(self, value: str) -> None:
        assert validate_url(value) == value

    @pytest.mark.parametrize(
        "value", ["example.com", "ftp://example.com", "not a url", 5, None]
    )
    def test_rejects_invalid_urls(self, value: Any) -> None:
        with pytest.raises(pydantic.ValidationError):
            validate_url(value)


class TestValidateEmail:
    def test_accepts_email_addresses(self) -> None:
        assert validate_email("john.doe@example.com") == "john.doe@example.com"

    @pytest.mark.parametrize("value", ["john.doe", "john@", 5])
    def test_rejects_invalid_email_addresses(self, value: Any) -> None:
        with pytest.raises(pydantic.ValidationError):
            validate_email(value)


class TestValidateList:
    def test_returns_lists(self) -> None:
        assert validate_list(["a", "b"]) == ["a", "b"]

    @pytest.mark.parametrize("value", ["a", ("a",), {"a": "b"}, None])
    def test_rejects_other_values(self, value: Any) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError, match="list of items"):
            validate_list(value)


class TestBuildEntryTypeModels:
    def test_builds_one_model_per_entry_type(self) -> None:
        assert list(every_kind_models) == ["every_kind", "child"]

    def test_models_carry_docs(self) -> None:
        model = every_kind_models["every_kind"]

        assert model.__doc__ == "The every_kind type."
        assert model.model_fields["title"].description == "The title."

    def test_optional_fields_default_to_none(self) -> None:
        model = every_kind_models["every_kind"].model_validate({"title": "Title"})

        fields = every_kind_entry_types["every_kind"].fields
        assert model.model_dump() == dict.fromkeys(fields) | {"title": "Title"}

    def test_rejects_missing_required_fields(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            every_kind_models["child"].model_validate({})

        assert exc_info.value.errors()[0]["type"] == "missing"

    def test_rejects_unknown_fields(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            every_kind_models["child"].model_validate({"name": "a", "nmae": "b"})

        assert exc_info.value.errors()[0]["type"] == "extra_forbidden"

    @pytest.mark.parametrize(
        ("field", "value", "expected_value"),
        [
            ("title", 2024, "2024"),
            ("code", "ABC", "ABC"),
            ("label", "anything", "anything"),
            ("when", "2020-05", DateValue(year=2020, month=5)),
            ("season", "Fall 2023", DateValue(text="Fall 2023")),
            ("link", "https://example.com", "https://example.com"),
            ("mail", "a@example.com", "a@example.com"),
            ("phone", "+14155550100", validate_phone("+14155550100")),
            ("amount", 3, 3),
            ("amount", 2.5, 2.5),
            ("visible", True, True),
            ("level", "high", "high"),
            ("tags", ["a", 1], ["a", "1"]),
            (
                "dates",
                ["2020", "present"],
                [DateValue(year=2020), DateValue(present=True)],
            ),
            ("levels", ["low", "high"], ["low", "high"]),
            (
                "points",
                ["Did a - with b", 5],
                [
                    Bullet(body="Did a", children=(Bullet(body="with b"),)),
                    Bullet(body="5"),
                ],
            ),
            (
                "children",
                [{"name": "Nested"}],
                [Entry(type_name="child", values={"name": "Nested"})],
            ),
        ],
    )
    def test_validates_every_field_kind(
        self, field: str, value: Any, expected_value: Any
    ) -> None:
        entry, errors = validate_every_kind(**{field: value})

        assert errors == []
        assert entry is not None
        assert entry.values[field] == expected_value

    @pytest.mark.parametrize(
        ("field", "value", "expected_location", "expected_message"),
        [
            ("title", ["a"], ("title",), "This should be text."),
            ("code", "abc", ("code",), "String should match pattern '[A-Z]{3}'"),
            ("label", 5, ("label",), "Input should be a valid string"),
            ("when", "Fall 2023", ("when",), "This is not a valid date."),
            ("link", "example.com", ("link",), "Input should be a valid URL"),
            ("mail", "a.example.com", ("mail",), "value is not a valid email"),
            ("phone", "12", ("phone",), "value is not a valid phone number"),
            ("amount", "many", ("amount", "int"), "Input should be a valid integer"),
            ("visible", "maybe", ("visible",), "Input should be a valid boolean"),
            ("level", "mid", ("level",), "Input should be 'low' or 'high'"),
            ("tags", "a", ("tags",), "Input should be a valid list"),
            ("dates", ["2020", "bad"], ("dates", 1), "This is not a valid date."),
            ("levels", ["mid"], ("levels", 0), "Input should be 'low' or 'high'"),
            ("points", "a", ("points",), "This should be a list of items."),
            ("points", [None], ("points",), "This should be text."),
            ("children", {"name": "a"}, ("children",), "list of items"),
        ],
    )
    def test_reports_invalid_values_at_their_field(
        self,
        field: str,
        value: Any,
        expected_location: tuple[str | int, ...],
        expected_message: str,
    ) -> None:
        entry, errors = validate_every_kind(**{field: value})

        assert entry is None
        assert errors[0]["loc"] == expected_location
        assert expected_message in errors[0]["msg"]

    def test_reports_problems_of_nested_entries(self) -> None:
        entry, errors = validate_every_kind(children=[{"nmae": "Nested"}])

        assert entry is None
        assert errors[0]["loc"] == ("children",)
        assert errors[0]["msg"] == (
            "This entry has problems: The entry type `child` has no field `nmae`."
            " Did you mean `name`?"
        )

    def test_nested_entries_need_a_known_entry_type(self) -> None:
        entry, errors = validate_every_kind(children=["Just text"])

        assert entry is None
        assert "there is no `paragraph` entry type" in errors[0]["msg"]

    def test_standard_models_validate_a_full_experience(
        self, standard_entry_type_models: EntryTypeModels
    ) -> None:
        model = standard_entry_type_models["experience"].model_validate(
            {
                "company": "ACME",
                "position": "Engineer",
                "start_date": "2020-01",
                "end_date": "present",
                "location": "Remote",
                "summary": "Built things.",
                "highlights": ["One", "Two - nested"],
            }
        )

        assert dict(model) == {
            "company": "ACME",
            "position": "Engineer",
            "date": None,
            "start_date": DateValue(year=2020, month=1),
            "end_date": DateValue(present=True),
            "location": "Remote",
            "summary": "Built things.",
            "highlights": [
                Bullet(body="One"),
                Bullet(body="Two", children=(Bullet(body="nested"),)),
            ],
        }


class TestDetectEntryType:
    @pytest.mark.parametrize(
        ("entry", "expected_type"),
        [
            ({"name": "Project"}, "normal"),
            ({"company": "ACME", "position": "Engineer"}, "experience"),
            ({"institution": "MIT", "area": "CS", "degree": "PhD"}, "education"),
            ({"title": "Paper", "authors": ["A"], "doi": "10.1/x"}, "publication"),
            ({"label": "Languages", "details": "English"}, "one_line"),
            ({"bullet": "Point"}, "bullet"),
            ({"number": "First"}, "numbered"),
            ({"reversed_number": "Last"}, "reversed_numbered"),
            ({"text": "Paragraph"}, "paragraph"),
            ({"name": "Project", "date": "2020", "highlights": ["a"]}, "normal"),
        ],
    )
    def test_detects_the_only_fitting_type(
        self,
        standard_entry_types: EntryTypes,
        entry: dict[str, Any],
        expected_type: str,
    ) -> None:
        assert detect_entry_type(entry, standard_entry_types) == (
            expected_type,
            [expected_type],
        )

    def test_explicit_type_wins(self, standard_entry_types: EntryTypes) -> None:
        assert detect_entry_type(
            {"type": "normal", "company": "ACME"}, standard_entry_types
        ) == ("normal", [])

    def test_unknown_explicit_type_is_not_detected(
        self, standard_entry_types: EntryTypes
    ) -> None:
        assert detect_entry_type(
            {"type": "talk", "name": "Project"}, standard_entry_types
        ) == (None, [])

    def test_reports_every_fitting_type_when_ambiguous(self) -> None:
        assert detect_entry_type({"title": "T", "date": "2020"}, twin_entry_types) == (
            None,
            ["talk", "award"],
        )

    @pytest.mark.parametrize(
        "entry",
        [
            {"company": "ACME"},
            {"company": "ACME", "position": "Engineer", "extra": "x"},
            {"nmae": "Project"},
        ],
    )
    def test_detects_nothing_when_no_type_fits(
        self, standard_entry_types: EntryTypes, entry: dict[str, Any]
    ) -> None:
        assert detect_entry_type(entry, standard_entry_types) == (None, [])


@pytest.mark.parametrize(
    ("entry", "expected_type"),
    [
        ({"company": "ACME", "positon": "Engineer"}, "experience"),
        ({"company": "ACME", "location": "Remote"}, "experience"),
        ({"institution": "MIT", "are": "CS"}, "education"),
        ({"title": "Paper", "author": ["A"]}, "publication"),
        ({"lable": "Languages", "details": "English"}, "one_line"),
        ({"nmae": "Project", "date": "2020"}, "normal"),
        # Misspelled fields count as the fields they're closest to:
        ({"bulet": "Point"}, "bullet"),
        ({"numbr": "First"}, "numbered"),
        ({"reverse_number": "Last"}, "reversed_numbered"),
        ({"txt": "Paragraph"}, "paragraph"),
        ({"compnay": "ACME", "positon": "Engineer"}, "experience"),
        # Nothing close: the first declared type among equals:
        ({"zzz": "?"}, "normal"),
    ],
)
def test_closest_entry_type(
    standard_entry_types: EntryTypes, entry: dict[str, Any], expected_type: str
) -> None:
    assert closest_entry_type(entry, standard_entry_types) == expected_type


class TestValidateEntry:
    def test_returns_the_entry_with_all_fields(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"label": "Languages", "details": "English, Turkish"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert errors == []
        assert entry == Entry(
            type_name="one_line",
            values={"label": "Languages", "details": "English, Turkish"},
        )

    @pytest.mark.parametrize(
        ("value", "expected_text"),
        [("Some **text**.", "Some **text**."), (2024, "2024"), (1.5, "1.5")],
    )
    def test_plain_text_is_a_paragraph(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        value: Any,
        expected_text: str,
    ) -> None:
        entry, errors = validate_entry(
            value, standard_entry_types, standard_entry_type_models
        )

        assert errors == []
        assert entry == Entry(type_name="paragraph", values={"text": expected_text})

    def test_plain_text_needs_a_paragraph_type(self) -> None:
        entry, errors = validate_entry("Text", twin_entry_types, twin_models)

        assert entry is None
        assert errors == [
            error_details(
                (),
                "An entry written as plain text is a paragraph, but there is no"
                " `paragraph` entry type.",
                "Text",
            )
        ]

    @pytest.mark.parametrize("value", [None, True, ["a", "b"]])
    def test_rejects_entries_that_are_not_mappings_or_text(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        value: Any,
    ) -> None:
        entry, errors = validate_entry(
            value, standard_entry_types, standard_entry_type_models
        )

        assert entry is None
        assert errors[0]["loc"] == ()
        assert errors[0]["msg"] == "An entry should be a mapping of fields or text."

    def test_rejects_empty_entries(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {}, standard_entry_types, standard_entry_type_models
        )

        assert entry is None
        assert errors[0]["msg"] == "This entry is empty."

    def test_rejects_entries_when_there_are_no_entry_types(self) -> None:
        entry, errors = validate_entry({"name": "Project"}, {}, {})

        assert entry is None
        assert errors[0]["loc"] == ()
        assert "There are no entry types" in errors[0]["msg"]

    @pytest.mark.parametrize(
        ("type_name", "expected_message"),
        [
            (
                "experiense",
                "There is no entry type `experiense`. Did you mean `experience`?",
            ),
            ("one-line", "There is no entry type `one-line`. Did you mean `one_line`?"),
            ("zzz", "There is no entry type `zzz`."),
        ],
    )
    def test_suggests_the_closest_type_for_an_unknown_type(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        type_name: str,
        expected_message: str,
    ) -> None:
        entry, errors = validate_entry(
            {"type": type_name, "name": "Project"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert errors == [error_details(("type",), expected_message, type_name)]

    def test_explicit_type_resolves_ambiguity(self) -> None:
        entry, errors = validate_entry(
            {"type": "award", "title": "Best Paper", "date": "2020"},
            twin_entry_types,
            twin_models,
        )

        assert errors == []
        assert entry == Entry(
            type_name="award",
            values={"title": "Best Paper", "date": DateValue(year=2020)},
        )

    def test_explicit_type_validates_against_that_type(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"type": "normal", "company": "ACME", "position": "Engineer"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert {error["loc"] for error in errors} == {
            ("company",),
            ("position",),
            ("name",),
        }

    def test_asks_for_a_type_when_several_fit(self) -> None:
        entry, errors = validate_entry(
            {"title": "Best Paper", "date": "2020"}, twin_entry_types, twin_models
        )

        assert entry is None
        assert errors[0]["loc"] == ()
        assert errors[0]["msg"] == (
            "This entry's fields fit several entry types (`talk`, `award`). Add"
            " `type:` to choose one."
        )

    def test_suggests_the_intended_field_for_a_typo(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"company": "ACME", "positon": "Engineer"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        # No "position is missing" error: the typo already explains it.
        assert errors == [
            error_details(
                ("positon",),
                "The entry type `experience` has no field `positon`. Did you mean"
                " `position`?",
                "Engineer",
            )
        ]

    @pytest.mark.parametrize(
        ("entry", "expected_message"),
        [
            (
                {"bulet": "Point"},
                "The entry type `bullet` has no field `bulet`. Did you mean `bullet`?",
            ),
            (
                {"txt": "Words"},
                "The entry type `paragraph` has no field `txt`. Did you mean `text`?",
            ),
        ],
    )
    def test_suggests_the_field_of_single_field_types(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        entry: dict[str, Any],
        expected_message: str,
    ) -> None:
        entry_value, errors = validate_entry(
            entry, standard_entry_types, standard_entry_type_models
        )

        assert entry_value is None
        assert [error["msg"] for error in errors] == [expected_message]

    def test_does_not_suggest_fields_the_entry_already_has(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"company": "ACME", "position": "Engineer", "positon": "Engineer"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert [error["msg"] for error in errors] == [
            "The entry type `experience` has no field `positon`."
        ]

    def test_reports_unknown_fields_and_invalid_values_together(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {
                "company": "ACME",
                "positon": "Engineer",
                "start_date": "bad",
                "highlights": "not a list",
            },
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert [error["loc"] for error in errors] == [
            ("positon",),
            ("start_date",),
            ("highlights",),
        ]

    def test_reports_missing_fields_of_the_closest_type(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"company": "ACME", "location": "Remote"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert [(error["loc"], error["type"]) for error in errors] == [
            (("position",), "missing")
        ]

    def test_leaves_the_type_key_out_of_the_values(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"type": "bullet", "bullet": "Point"},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert errors == []
        assert entry == Entry(type_name="bullet", values={"bullet": "Point"})

    def test_keeps_typst_bullets_whole(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
    ) -> None:
        entry, errors = validate_entry(
            {"name": "Math", "highlights": [TypstString("$a - b$ - c"), "d - e"]},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert errors == []
        assert entry is not None
        assert entry.values["highlights"] == [
            Bullet(body="$a - b$ - c"),
            Bullet(body="d", children=(Bullet(body="e"),)),
        ]

    @pytest.mark.parametrize(
        ("start_date", "end_date"),
        [
            ("2021-01-01", "2020-01-01"),
            ("2020-02", "2020-01"),
            (2021, "2020-12-31"),
            ("present", "2020"),
        ],
    )
    def test_rejects_starting_after_ending(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        start_date: Any,
        end_date: Any,
    ) -> None:
        entry, errors = validate_entry(
            {"name": "Project", "start_date": start_date, "end_date": end_date},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert entry is None
        assert errors[0]["loc"] == ("start_date",)
        assert errors[0]["msg"] == "`start_date` cannot be after `end_date`."

    @pytest.mark.parametrize(
        ("start_date", "end_date"),
        [
            ("2020-01-01", "2020-01-01"),
            ("2020-01", "2020-01-15"),
            ("2020", "present"),
            ("2020-05", None),
            (None, "2020-05"),
        ],
    )
    def test_accepts_dates_in_order(
        self,
        standard_entry_types: EntryTypes,
        standard_entry_type_models: EntryTypeModels,
        start_date: Any,
        end_date: Any,
    ) -> None:
        entry, errors = validate_entry(
            {"name": "Project", "start_date": start_date, "end_date": end_date},
            standard_entry_types,
            standard_entry_type_models,
        )

        assert errors == []
        assert entry is not None


@pytest.mark.parametrize(
    ("values", "expected_input"),
    [
        (
            {
                "start_date": DateValue(year=2021),
                "end_date": DateValue(year=2020, month=6),
            },
            "2021-01-01 > 2020-06-01",
        ),
        ({"start_date": DateValue(year=2020), "end_date": DateValue(year=2021)}, None),
        ({"start_date": DateValue(year=2021)}, None),
        ({"end_date": DateValue(year=2021)}, None),
        (
            {
                "start_date": DateValue(text="Fall 2023"),
                "end_date": DateValue(year=2020),
            },
            None,
        ),
        ({"start_date": "2021", "end_date": "2020"}, None),
        ({}, None),
    ],
)
def test_check_date_order(values: dict[str, Any], expected_input: str | None) -> None:
    error = check_date_order(values)

    if expected_input is None:
        assert error is None
    else:
        assert error == error_details(
            ("start_date",), "`start_date` cannot be after `end_date`.", expected_input
        )


def test_error_details() -> None:
    assert error_details(("a", 0), "Message.", "value") == {
        "type": "rendercv_entry",
        "loc": ("a", 0),
        "msg": "Message.",
        "input": "value",
    }
