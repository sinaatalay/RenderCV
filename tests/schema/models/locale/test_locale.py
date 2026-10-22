import json
import pathlib
from typing import Any

import pydantic
import pytest
import typst

from rendercv.schema.models.locale.locale import (
    Locale,
    Phrases,
    available_locales,
    default_locale,
    get_built_in_locales,
    locales_directory,
)
from rendercv.schema.yaml_reader import read_yaml

locale_files = sorted(locales_directory.glob("*.yaml"))
rtl_languages = {"arabic", "hebrew", "persian"}


def write_degree_with_area(phrase: str, tmp_path: pathlib.Path) -> str:
    # Evaluates a phrase the way the standard education entry type does:
    main = tmp_path / "main.typ"
    main.write_text(
        f"#let phrase = {json.dumps(phrase, ensure_ascii=False)}\n"
        '#let written = eval(phrase, mode: "markup", scope: (degree: [PhD], area:'
        " [CS]))\n"
        '#metadata(written.children.map(child => if child.has("text") {'
        ' child.text } else { " " }).join()) <written>\n',
        encoding="utf-8",
    )
    return json.loads(typst.query(str(main), "<written>", field="value", one=True))


class TestGetBuiltInLocales:
    def test_reads_every_file(self) -> None:
        assert list(get_built_in_locales()) == [file.stem for file in locale_files]
        assert available_locales == tuple(get_built_in_locales())
        assert "english" in available_locales

    @pytest.mark.parametrize("file", locale_files, ids=lambda file: file.stem)
    def test_every_file_defines_every_field(self, file: pathlib.Path) -> None:
        # A missing field would silently fall back to nothing, not to English:
        data = read_yaml(file)

        assert set(data) == set(Locale.model_fields)
        assert set(data["phrases"]) == set(Phrases.model_fields)
        assert data["language"] == file.stem

    @pytest.mark.parametrize("language", available_locales)
    def test_every_built_in_locale_is_valid(self, language: str) -> None:
        locale = Locale.model_validate({"language": language})

        assert locale.language == language
        assert locale.direction == ("rtl" if language in rtl_languages else "ltr")
        assert "#degree" in locale.phrases.degree_with_area
        assert "#area" in locale.phrases.degree_with_area


def test_default_locale() -> None:
    locale = default_locale()

    assert locale.language == "english"
    assert locale.iso_code == "en"
    assert locale.month_names[0] == "January"
    assert locale == Locale.model_validate({})


class TestLocale:
    def test_overrides_fields_of_a_built_in_language(self) -> None:
        locale = Locale.model_validate({"language": "english", "present": "now"})

        assert locale.present == "now"
        assert locale.last_updated == "Last updated in"

    def test_merges_phrases_with_the_built_in_ones(self) -> None:
        locale = Locale.model_validate(
            {"language": "turkish", "phrases": {"degree_with_area": "#degree: #area"}}
        )

        assert locale.phrases.degree_with_area == "#degree: #area"
        assert locale.present == get_built_in_locales()["turkish"]["present"]

    def test_empty_phrases_keep_the_built_in_ones(self) -> None:
        locale = Locale.model_validate({"language": "turkish", "phrases": None})

        assert locale.phrases.degree_with_area == "#area, #degree"

    def test_accepts_a_custom_language_with_every_field(self) -> None:
        english = get_built_in_locales()["english"]

        locale = Locale.model_validate(
            {**english, "language": "klingon", "iso_code": "tlh", "present": "DaH"}
        )

        assert locale.language == "klingon"
        assert locale.present == "DaH"

    def test_accepts_locale_instances(self) -> None:
        locale = default_locale()

        assert Locale.model_validate(locale) == locale

    @pytest.mark.parametrize("value", ["english", None, ["english"]])
    def test_rejects_values_that_are_not_mappings(self, value: Any) -> None:
        with pytest.raises(pydantic.ValidationError):
            Locale.model_validate(value)

    def test_json_schema_requires_nothing(self) -> None:
        # `locale: {language: german}` is complete, so editors must accept it:
        assert Locale.model_json_schema()["required"] == []

    def test_custom_language_needs_every_field(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Locale.model_validate({"language": "klingon"})

        (error,) = exc_info.value.errors()
        assert "no built-in language `klingon`" in error["msg"]
        for field in set(Locale.model_fields) - {"language", "direction"}:
            assert field in error["msg"]

    def test_suggests_a_built_in_language_for_a_typo(self) -> None:
        with pytest.raises(pydantic.ValidationError, match="Did you mean `english`"):
            Locale.model_validate({"language": "englsh"})

    def test_accepts_a_complete_custom_language(self) -> None:
        english = default_locale().model_dump()
        locale = Locale.model_validate(english | {"language": "klingon"})

        assert locale.language == "klingon"

    @pytest.mark.parametrize(
        ("value", "expected_location"),
        [
            ({"month_names": ["January"]}, ("month_names",)),
            ({"month_abbreviations": list("abcdefghijklm")}, ("month_abbreviations",)),
            ({"direction": "up"}, ("direction",)),
            ({"phrases": "#degree in #area"}, ("phrases",)),
            ({"phrases": {"degree_with_area": 5}}, ("phrases", "degree_with_area")),
            ({"phrases": {"degree": "x"}}, ("phrases", "degree")),
            ({"language": ["english"]}, ("language",)),
            ({"lanugage": "english"}, ("lanugage",)),
        ],
    )
    def test_rejects_invalid_values(
        self, value: dict[str, Any], expected_location: tuple[str, ...]
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Locale.model_validate({"language": "english", **value})

        assert expected_location in [error["loc"] for error in exc_info.value.errors()]


class TestPhrases:
    @pytest.mark.parametrize(
        ("phrase", "expected_phrase"),
        [
            ("DEGREE in AREA", "#degree; in #area;"),
            ("AREA, DEGREE", "#area;, #degree;"),
            ("DEGREE AREA szakon", "#degree; #area; szakon"),
            ("DEGREE בAREA", "#degree; ב#area;"),
            ("#degree in #area", "#degree in #area"),
            ("#area (DEGREE)", "#area (DEGREE)"),
        ],
    )
    def test_converts_rendercv_2_placeholders(
        self, phrase: str, expected_phrase: str
    ) -> None:
        phrases = Phrases.model_validate({"degree_with_area": phrase})

        assert phrases.degree_with_area == expected_phrase

    @pytest.mark.parametrize(
        ("phrase", "expected_text"),
        [
            ("DEGREE in AREA", "PhD in CS"),
            ("AREA, DEGREE", "CS, PhD"),
            ("DEGREE בAREA", "PhD בCS"),
            ("DEGREE; AREA", "PhD; CS"),
            ("AREAszakon DEGREE", "CSszakon PhD"),
        ],
    )
    def test_converted_phrases_write_the_same_text_in_typst(
        self, tmp_path: pathlib.Path, phrase: str, expected_text: str
    ) -> None:
        converted = Phrases.model_validate({"degree_with_area": phrase})

        written = write_degree_with_area(converted.degree_with_area, tmp_path)

        assert written == expected_text

    @pytest.mark.parametrize("language", available_locales)
    def test_built_in_phrases_compile_in_typst(
        self, tmp_path: pathlib.Path, language: str
    ) -> None:
        phrase = Locale.model_validate({"language": language}).phrases.degree_with_area

        written = write_degree_with_area(phrase, tmp_path)

        assert "PhD" in written
        assert "CS" in written
