import json
import pathlib
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.renderer.document import (
    as_list,
    build_document_data,
    clean_url,
    data_format_version,
    encode_bullet,
    encode_connections,
    encode_date,
    encode_entry,
    encode_section,
    encode_value,
    photo_import_path,
    text_connection,
)
from rendercv.renderer.project import Project
from rendercv.schema.models.cv.entry_types import (
    Bullet,
    DateValue,
    Entry,
    EntryTypeDeclaration,
    FieldDeclaration,
    PhoneValue,
)
from rendercv.schema.models.cv.section import Section
from rendercv.schema.models.rendercv_model import RenderCVModel

type BuildModel = Callable[..., RenderCVModel]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.com", "example.com"),
        ("https://www.example.com/", "example.com"),
        ("http://example.com/path/", "example.com/path"),
        ("www.example.com", "example.com"),
        ("example.com", "example.com"),
        ("https://example.com/a?b=c", "example.com/a?b=c"),
    ],
)
def test_clean_url(url: str, expected: str) -> None:
    assert clean_url(url) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (DateValue(year=2020), {"year": 2020}),
        (DateValue(year=2020, month=5), {"year": 2020, "month": 5}),
        (
            DateValue(year=2020, month=5, day=17),
            {"year": 2020, "month": 5, "day": 17},
        ),
        (DateValue(present=True), {"present": True}),
        (DateValue(text="Fall **2023**"), {"text": ["Fall ", {"strong": ["2023"]}]}),
    ],
)
def test_encode_date(value: DateValue, expected: dict[str, Any]) -> None:
    assert encode_date(value) == expected


def test_encode_bullet() -> None:
    bullet = Bullet(
        body="Published **papers**",
        children=(Bullet(body="ICML"), Bullet(body="NeurIPS")),
    )

    assert encode_bullet(bullet) == {
        "body": ["Published ", {"strong": ["papers"]}],
        "children": [
            {"body": ["ICML"], "children": []},
            {"body": ["NeurIPS"], "children": []},
        ],
    }


sample_phone = PhoneValue(
    e164="+16095550100",
    international="+1 609-555-0100",
    national="(609) 555-0100",
    uri="tel:+1-609-555-0100",
)


class TestEncodeValue:
    @pytest.mark.parametrize(
        ("value", "field", "expected"),
        [
            (None, FieldDeclaration(kind="markdown"), None),
            ("**a**", FieldDeclaration(kind="markdown"), [{"strong": ["a"]}]),
            (
                DateValue(year=2020, month=1),
                FieldDeclaration(kind="date"),
                {"year": 2020, "month": 1},
            ),
            (
                sample_phone,
                FieldDeclaration(kind="phone"),
                {
                    "e164": "+16095550100",
                    "international": "+1 609-555-0100",
                    "national": "(609) 555-0100",
                    "uri": "tel:+1-609-555-0100",
                },
            ),
            (
                [Bullet(body="a", children=(Bullet(body="b"),))],
                FieldDeclaration(kind="bullets"),
                [{"body": ["a"], "children": [{"body": ["b"], "children": []}]}],
            ),
            (
                ["a", "*b*"],
                FieldDeclaration(kind="list", of="markdown"),
                [["a"], [{"emph": ["b"]}]],
            ),
            (["a", "*b*"], FieldDeclaration(kind="list"), [["a"], [{"emph": ["b"]}]]),
            (["a", "*b*"], FieldDeclaration(kind="list", of="text"), ["a", "*b*"]),
            (
                [DateValue(year=2020)],
                FieldDeclaration(kind="list", of="date"),
                [{"year": 2020}],
            ),
            ("*raw*", FieldDeclaration(kind="text"), "*raw*"),
            ("https://x.com", FieldDeclaration(kind="url"), "https://x.com"),
            ("a@b.com", FieldDeclaration(kind="email"), "a@b.com"),
            (3.5, FieldDeclaration(kind="number"), 3.5),
            (True, FieldDeclaration(kind="bool"), True),
            ("b", FieldDeclaration(kind="choice", choices=("a", "b")), "b"),
        ],
    )
    def test_encodes_each_field_kind(
        self, value: Any, field: FieldDeclaration, expected: Any
    ) -> None:
        assert encode_value(value, field, {}) == expected

    def test_encodes_nested_entries(
        self, standard_entry_types: dict[str, EntryTypeDeclaration]
    ) -> None:
        entry = Entry(type_name="one_line", values={"label": "A", "details": "*B*"})

        assert encode_value(
            [entry], FieldDeclaration(kind="entries"), standard_entry_types
        ) == [
            {
                "type": "one_line",
                "fields": {"label": ["A"], "details": [{"emph": ["B"]}]},
            }
        ]


def test_encode_entry(standard_entry_types: dict[str, EntryTypeDeclaration]) -> None:
    entry = Entry(
        type_name="normal",
        values={
            "name": "Project",
            "date": None,
            "start_date": DateValue(year=2020, month=1),
            "end_date": DateValue(present=True),
            "location": None,
            "summary": None,
            "highlights": [Bullet(body="Did things")],
        },
    )

    assert encode_entry(entry, standard_entry_types) == {
        "type": "normal",
        "fields": {
            "name": ["Project"],
            "start_date": {"year": 2020, "month": 1},
            "end_date": {"present": True},
            "highlights": [{"body": ["Did things"], "children": []}],
        },
    }


def test_encode_section(standard_entry_types: dict[str, EntryTypeDeclaration]) -> None:
    section = Section(
        title="Work **Experience**",
        key="work_experience",
        subsections=(
            Section(
                title="Industry",
                key="industry",
                entries=(Entry(type_name="paragraph", values={"text": "Text"}),),
            ),
        ),
    )

    assert encode_section(section, standard_entry_types) == {
        "key": "work_experience",
        "title": ["Work ", {"strong": ["Experience"]}],
        "entries": [],
        "subsections": [
            {
                "key": "industry",
                "title": ["Industry"],
                "entries": [{"type": "paragraph", "fields": {"text": ["Text"]}}],
                "subsections": [],
            }
        ],
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        ("a", ["a"]),
        (["a", "b"], ["a", "b"]),
        (("a", "b"), ["a", "b"]),
    ],
)
def test_as_list(value: Any, expected: list[Any]) -> None:
    assert as_list(value) == expected


@pytest.mark.parametrize(
    ("kind", "text", "url", "expected_url_text"),
    [
        ("website", "example.com", "https://www.example.com/", "example.com"),
        ("email", "a@b.com", "mailto:a@b.com", "a@b.com"),
        ("phone", "(609) 555-0100", "tel:+1-609-555-0100", "(609) 555-0100"),
        ("location", "Istanbul", None, "Istanbul"),
    ],
)
def test_text_connection(
    kind: str, text: str, url: str | None, expected_url_text: str
) -> None:
    connection = text_connection(kind, text, url)

    assert connection["kind"] == kind
    assert connection["icon"]
    assert connection["url"] == url
    assert connection["text"] == [text]
    assert connection["url_text"] == expected_url_text


connections_cv: dict[str, Any] = {
    "name": "Jane Doe",
    "website": ["https://www.jane.dev/", "https://blog.jane.dev"],
    "phone": ["+1 609 555 0100", "+90 532 123 45 67"],
    "email": ["jane@doe.com", "jane@work.com"],
    "location": "Istanbul, **Türkiye**",
    "social_networks": [
        {"network": "GitHub", "username": "jane"},
        {"network": "LinkedIn", "username": "janedoe"},
    ],
    "custom_connections": [
        {
            "placeholder": "Book a **call**",
            "url": "https://cal.com/jane",
            "fontawesome_icon": "calendar-days",
        },
        {"placeholder": "Available", "fontawesome_icon": "star"},
    ],
}


class TestEncodeConnections:
    def test_follows_the_order_of_the_yaml(self, build_model: BuildModel) -> None:
        model = build_model(connections_cv)

        connections = encode_connections(model, list(connections_cv))

        assert [connection["kind"] for connection in connections] == [
            "website",
            "website",
            "phone",
            "phone",
            "email",
            "email",
            "location",
            "social",
            "social",
            "custom",
            "custom",
        ]

    def test_leaves_out_keys_not_in_the_order(self, build_model: BuildModel) -> None:
        model = build_model(connections_cv)

        connections = encode_connections(model, ["email", "location"])

        assert [connection["kind"] for connection in connections] == [
            "email",
            "email",
            "location",
        ]

    def test_encodes_every_connection(self, build_model: BuildModel) -> None:
        model = build_model(connections_cv)

        connections = encode_connections(model, list(connections_cv))

        assert connections == [
            {
                "kind": "website",
                "icon": "link",
                "url": "https://www.jane.dev/",
                "text": ["jane.dev"],
                "url_text": "jane.dev",
            },
            {
                "kind": "website",
                "icon": "link",
                "url": "https://blog.jane.dev",
                "text": ["blog.jane.dev"],
                "url_text": "blog.jane.dev",
            },
            {
                "kind": "phone",
                "icon": "phone",
                "url": "tel:+1-609-555-0100",
                "text": ["(609) 555-0100"],
                "url_text": "(609) 555-0100",
                "phone": {
                    "e164": "+16095550100",
                    "international": "+1 609-555-0100",
                    "national": "(609) 555-0100",
                    "uri": "tel:+1-609-555-0100",
                },
            },
            {
                "kind": "phone",
                "icon": "phone",
                "url": "tel:+90-532-123-45-67",
                "text": ["0532 123 45 67"],
                "url_text": "0532 123 45 67",
                "phone": {
                    "e164": "+905321234567",
                    "international": "+90 532 123 45 67",
                    "national": "0532 123 45 67",
                    "uri": "tel:+90-532-123-45-67",
                },
            },
            {
                "kind": "email",
                "icon": "envelope",
                "url": "mailto:jane@doe.com",
                "text": ["jane@doe.com"],
                "url_text": "jane@doe.com",
            },
            {
                "kind": "email",
                "icon": "envelope",
                "url": "mailto:jane@work.com",
                "text": ["jane@work.com"],
                "url_text": "jane@work.com",
            },
            {
                "kind": "location",
                "icon": "location-dot",
                "url": None,
                "text": ["Istanbul, ", {"strong": ["Türkiye"]}],
            },
            {
                "kind": "social",
                "network": "GitHub",
                "icon": "github",
                "url": "https://github.com/jane",
                "text": ["jane"],
                "url_text": "github.com/jane",
            },
            {
                "kind": "social",
                "network": "LinkedIn",
                "icon": "linkedin",
                "url": "https://linkedin.com/in/janedoe",
                "text": ["janedoe"],
                "url_text": "linkedin.com/in/janedoe",
            },
            {
                "kind": "custom",
                "icon": "calendar-days",
                "url": "https://cal.com/jane",
                "text": ["Book a ", {"strong": ["call"]}],
                "url_text": "cal.com/jane",
            },
            {
                "kind": "custom",
                "icon": "star",
                "url": None,
                "text": ["Available"],
                "url_text": "Available",
            },
        ]

    def test_encodes_single_values(self, build_model: BuildModel) -> None:
        model = build_model(
            {
                "email": "jane@doe.com",
                "phone": "+1 609 555 0100",
                "website": "https://jane.dev",
            }
        )

        connections = encode_connections(model, ["email", "phone", "website"])

        assert [connection["url"] for connection in connections] == [
            "mailto:jane@doe.com",
            "tel:+1-609-555-0100",
            "https://jane.dev",
        ]

    def test_skips_missing_fields(self, build_model: BuildModel) -> None:
        model = build_model({"name": "Jane Doe"})

        assert encode_connections(model, list(connections_cv)) == []


class TestBuildDocumentData:
    def test_builds_the_header(self, build_model: BuildModel) -> None:
        model = build_model(
            {
                "name": "Jane **Doe**",
                "headline": "Engineer at *Acme*",
                "email": "jane@doe.com",
            }
        )

        data = build_document_data(model, {}, connection_order=["email"])

        assert data["version"] == data_format_version
        assert data["header"]["name"] == ["Jane ", {"strong": ["Doe"]}]
        assert data["header"]["plain_name"] == "Jane Doe"
        assert data["header"]["headline"] == ["Engineer at ", {"emph": ["Acme"]}]
        assert data["header"]["photo"] is None
        assert [c["kind"] for c in data["header"]["connections"]] == ["email"]

    def test_leaves_out_missing_name_and_headline(
        self, build_model: BuildModel
    ) -> None:
        data = build_document_data(build_model({}), {}, connection_order=[])

        assert data["header"]["name"] is None
        assert data["header"]["plain_name"] is None
        assert data["header"]["headline"] is None
        assert data["header"]["connections"] == []
        assert data["sections"] == []

    def test_passes_the_photo_path(self, build_model: BuildModel) -> None:
        data = build_document_data(
            build_model({}), {}, connection_order=[], photo="/photo.jpg"
        )

        assert data["header"]["photo"] == "/photo.jpg"

    def test_builds_the_settings(self, build_model: BuildModel) -> None:
        model = build_model(
            {"name": "Jane Doe"},
            settings={
                "bold_keywords": ["Python", "C++", "Python"],
                "pdf_title": "NAME_IN_SNAKE_CASE - CV - MONTH_NAME YEAR",
            },
        )

        data = build_document_data(model, {}, connection_order=[])

        assert data["settings"] == {
            "current_date": {"year": 2025, "month": 6, "day": 1},
            "bold_keywords": ["Python", "C++"],
            "pdf_title": "Jane_Doe - CV - June 2025",
        }

    def test_passes_the_locale(self, build_model: BuildModel) -> None:
        model = build_model({}, locale={"language": "german", "present": "heute"})

        data = build_document_data(model, {}, connection_order=[])

        assert data["locale"]["language"] == "german"
        assert data["locale"]["iso_code"] == "de"
        assert data["locale"]["present"] == "heute"
        assert data["locale"]["month_names"][2] == "März"
        assert data["locale"]["phrases"] == {"degree_with_area": "#degree in #area"}

    def test_builds_sections_and_subsections(
        self,
        build_model: BuildModel,
        standard_entry_types: dict[str, EntryTypeDeclaration],
    ) -> None:
        model = build_model(
            {
                "sections": {
                    "summary": ["I build **things**."],
                    "experience": {
                        "Industry": [
                            {
                                "company": "Acme",
                                "position": "Engineer",
                                "start_date": "2020-01",
                                "end_date": "present",
                                "highlights": ["Built - nested one - nested two"],
                            }
                        ],
                        "Academia": [{"bullet": "Taught"}],
                    },
                }
            }
        )

        data = build_document_data(model, standard_entry_types, connection_order=[])

        assert data["sections"] == [
            {
                "key": "summary",
                "title": ["Summary"],
                "entries": [
                    {
                        "type": "paragraph",
                        "fields": {"text": ["I build ", {"strong": ["things"]}, "."]},
                    }
                ],
                "subsections": [],
            },
            {
                "key": "experience",
                "title": ["Experience"],
                "entries": [],
                "subsections": [
                    {
                        "key": "industry",
                        "title": ["Industry"],
                        "entries": [
                            {
                                "type": "experience",
                                "fields": {
                                    "company": ["Acme"],
                                    "position": ["Engineer"],
                                    "start_date": {"year": 2020, "month": 1},
                                    "end_date": {"present": True},
                                    "highlights": [
                                        {
                                            "body": ["Built"],
                                            "children": [
                                                {
                                                    "body": ["nested one"],
                                                    "children": [],
                                                },
                                                {
                                                    "body": ["nested two"],
                                                    "children": [],
                                                },
                                            ],
                                        }
                                    ],
                                },
                            }
                        ],
                        "subsections": [],
                    },
                    {
                        "key": "academia",
                        "title": ["Academia"],
                        "entries": [
                            {"type": "bullet", "fields": {"bullet": ["Taught"]}}
                        ],
                        "subsections": [],
                    },
                ],
            },
        ]

    def test_is_json_serializable(self, sample_project: Project) -> None:
        assert json.loads(json.dumps(sample_project.data)) == sample_project.data

    def test_matches_the_sample_cv_snapshot(
        self,
        sample_project: Project,
        testdata_dir: pathlib.Path,
        update_testdata: bool,
    ) -> None:
        reference_path = testdata_dir / "sample_cv.json"
        data_json = json.dumps(sample_project.data, indent=2, ensure_ascii=False)

        if update_testdata:
            reference_path.parent.mkdir(parents=True, exist_ok=True)
            reference_path.write_text(data_json + "\n", encoding="utf-8")

        assert data_json + "\n" == reference_path.read_text(encoding="utf-8")


def test_photo_import_path(tmp_path: pathlib.Path) -> None:
    photo = tmp_path / "images" / "photo.jpg"

    assert photo_import_path(photo, tmp_path) == "/images/photo.jpg"
