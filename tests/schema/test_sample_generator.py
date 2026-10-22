import pathlib
from collections.abc import Callable, Mapping

import pytest

from rendercv import __version__
from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.project import Project
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.models.cv.entry_types import DateValue, EntryTypeDeclaration
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_entries_file,
    create_sample_yaml_input_file,
    get_built_in_design_names,
    sample_content_path,
)
from rendercv.schema.yaml_reader import read_yaml

type RenderPdf = Callable[[pathlib.Path], tuple[Project, pathlib.Path]]
type EntryTypes = Mapping[str, EntryTypeDeclaration]

built_in_design_names = (
    "classic",
    "ember",
    "engineeringclassic",
    "engineeringresumes",
    "harvard",
    "ink",
    "moderncv",
    "opal",
    "sb2nov",
)


def write_project(
    folder: pathlib.Path, yaml: str, *, design: str = "", entries: str = ""
) -> pathlib.Path:
    yaml_file = folder / "cv.yaml"
    yaml_file.write_text(yaml, encoding="utf-8")
    if design:
        (folder / "design.typ").write_text(design, encoding="utf-8")
    if entries:
        (folder / "entries.typ").write_text(entries, encoding="utf-8")
    return yaml_file


def test_get_built_in_design_names() -> None:
    assert sorted(get_built_in_design_names()) == sorted(built_in_design_names)


class TestCreateSampleYamlInputFile:
    def test_starts_with_the_schema_of_this_version(self) -> None:
        first_line = create_sample_yaml_input_file().splitlines()[0]

        assert first_line == (
            "# yaml-language-server:"
            " $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/"
            f"v{__version__}/schema.json"
        )

    def test_uses_the_sample_content(self) -> None:
        sample = read_yaml(create_sample_yaml_input_file())

        assert sample["cv"] == read_yaml(sample_content_path)["cv"]
        assert "design" not in sample

    @pytest.mark.parametrize(
        "name", ["John Doe", "Matías Ñandú", 'Jane "JJ" Doe', "Doe: John", "李小龍"]
    )
    def test_writes_the_name(self, name: str) -> None:
        sample = read_yaml(create_sample_yaml_input_file(name=name))

        assert sample["cv"]["name"] == name

    @pytest.mark.parametrize("locale", available_locales)
    def test_is_valid_for_every_locale(
        self, standard_entry_types: EntryTypes, locale: str
    ) -> None:
        _, model = build_rendercv_dictionary_and_model(
            create_sample_yaml_input_file(locale=locale),
            entry_types=standard_entry_types,
        )

        assert model.locale.language == locale
        assert model.cv.name == "John Doe"

    def test_shows_every_standard_entry_type(
        self, standard_entry_types: EntryTypes
    ) -> None:
        _, model = build_rendercv_dictionary_and_model(
            create_sample_yaml_input_file(), entry_types=standard_entry_types
        )

        assert model.cv.sections is not None
        used_types = {
            entry.type_name
            for section in model.cv.sections
            for entry in section.entries
        }
        assert used_types == set(standard_entry_types)

    def test_rejects_unknown_locales(self) -> None:
        with pytest.raises(RenderCVUserError, match="`klingon` is not built in"):
            create_sample_yaml_input_file(locale="klingon")

    @pytest.mark.parametrize("locale", ["english", "arabic", "japanese"])
    def test_renders(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf, locale: str
    ) -> None:
        yaml_file = write_project(
            tmp_path, create_sample_yaml_input_file(locale=locale)
        )

        project, pdf = render_pdf(yaml_file)

        assert project.model.locale.language == locale
        assert pdf.parent == tmp_path / "rendercv_output"


class TestCreateSampleDesignFile:
    @pytest.mark.parametrize("design", built_in_design_names)
    def test_imports_the_design(self, design: str) -> None:
        source = create_sample_design_file(design)

        assert (
            f'#import "@preview/rendercv:{get_rendercv_typst_version()}": designs'
            in source
        )
        assert f"#let design = designs.{design}(" in source

    @pytest.mark.parametrize("design", built_in_design_names)
    def test_renders_with_every_design(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf, design: str
    ) -> None:
        yaml_file = write_project(
            tmp_path,
            create_sample_yaml_input_file(),
            design=create_sample_design_file(design),
        )

        project, _ = render_pdf(yaml_file)

        assert project.typst_project.design_file_path == tmp_path / "design.typ"

    def test_rejects_unknown_designs(self) -> None:
        with pytest.raises(RenderCVUserError) as exc_info:
            create_sample_design_file("fancy")

        assert exc_info.value.message == (
            "There is no built-in design `fancy`. Built-in designs:"
            f" {', '.join(get_built_in_design_names())}."
        )


class TestCreateSampleEntriesFile:
    def test_imports_the_standard_entry_types(self) -> None:
        source = create_sample_entries_file()

        assert (
            f'#import "@preview/rendercv:{get_rendercv_typst_version()}": *' in source
        )
        assert "#let talk = entry-type(" in source

    def test_defines_a_talk_entry_type_that_renders(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf
    ) -> None:
        yaml_file = write_project(
            tmp_path,
            "cv:\n"
            "  name: John Doe\n"
            "  sections:\n"
            "    talks:\n"
            "      - title: Typst for CVs\n"
            "        event: TypstConf\n"
            "        date: 2024-05\n"
            "        slides: https://example.com/slides\n"
            "      - title: Without slides\n"
            "        event: Meetup\n"
            "        date: 2023\n"
            "    experience:\n"
            "      - company: ACME\n"
            "        position: Engineer\n",
            entries=create_sample_entries_file(),
        )

        project, _ = render_pdf(yaml_file)

        assert "talk" in project.entry_types
        # The standard types are still there:
        assert set(project.entry_types) >= {"normal", "experience", "paragraph"}
        assert project.model.cv.sections is not None
        talks, experience = project.model.cv.sections
        assert [entry.type_name for entry in talks.entries] == ["talk", "talk"]
        assert talks.entries[0].values["date"] == DateValue(year=2024, month=5)
        assert talks.entries[1].values["slides"] is None
        assert experience.entries[0].type_name == "experience"

    def test_validates_talks_against_their_fields(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf
    ) -> None:
        yaml_file = write_project(
            tmp_path,
            "cv:\n"
            "  sections:\n"
            "    talks:\n"
            "      - title: Typst for CVs\n"
            "        event: TypstConf\n"
            "        date: 2024-05\n"
            "        slids: https://example.com/slides\n",
            entries=create_sample_entries_file(),
        )

        with pytest.raises(RenderCVUserValidationError) as exc_info:
            render_pdf(yaml_file)

        (error,) = exc_info.value.validation_errors
        assert error.message == (
            "The entry type `talk` has no field `slids`. Did you mean `slides`?"
        )
