import pathlib

import pytest

from rendercv.api import (
    Problem,
    available_output_formats,
    problems_from_error,
    render,
    validate,
)
from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    RenderCVValidationError,
)
from rendercv.renderer.typst_packages import get_rendercv_typst_version

version = get_rendercv_typst_version()


@pytest.fixture
def input_file(tmp_path: pathlib.Path) -> pathlib.Path:
    file = tmp_path / "cv.yaml"
    file.write_text(
        "cv:\n"
        "  name: Jane Doe\n"
        "  sections:\n"
        "    Skills:\n"
        "      - bullet: Typst\n"
        "settings:\n"
        "  current_date: 2024-06-15\n",
        encoding="utf-8",
    )
    return file


class TestRender:
    def test_renders_every_format(self, input_file: pathlib.Path) -> None:
        cv = render(input_file, formats=available_output_formats)

        assert cv.pdf is not None
        assert cv.pdf.startswith(b"%PDF-")
        assert cv.png is not None
        assert len(cv.png) == 1
        assert cv.png[0].startswith(b"\x89PNG")
        assert cv.svg is not None
        assert cv.svg[0].startswith("<svg")
        assert cv.html is not None
        assert "Jane Doe" in cv.html
        assert cv.markdown is not None
        assert cv.markdown.startswith("# Jane Doe")
        assert "- Typst" in cv.markdown
        assert cv.typst is not None
        assert f'#import "@preview/rendercv:{version}" as rendercv' in cv.typst

    def test_renders_only_pdf_by_default(self, input_file: pathlib.Path) -> None:
        cv = render(input_file)

        assert cv.pdf is not None
        assert (cv.png, cv.svg, cv.html, cv.markdown, cv.typst) == (None,) * 5

    def test_writes_nothing_next_to_the_input_file(
        self, input_file: pathlib.Path
    ) -> None:
        render(input_file, formats=available_output_formats)

        assert sorted(path.name for path in input_file.parent.iterdir()) == ["cv.yaml"]

    def test_uses_the_design_file_next_to_the_input_file(
        self, input_file: pathlib.Path
    ) -> None:
        classic = render(input_file, formats=("typst",)).typst
        (input_file.parent / "design.typ").write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            "#let design = designs.moderncv()\n",
            encoding="utf-8",
        )

        cv = render(input_file, formats=("typst",))

        assert cv.typst != classic
        assert '#import "/design.typ" as design-file' in (cv.typst or "")

    def test_takes_design_and_entries_files(
        self, input_file: pathlib.Path, tmp_path: pathlib.Path
    ) -> None:
        other_folder = tmp_path / "other"
        other_folder.mkdir()
        design_file = other_folder / "short.typ"
        design_file.write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            "#let design = designs.sb2nov()\n",
            encoding="utf-8",
        )
        entries_file = other_folder / "types.typ"
        entries_file.write_text(
            f'#import "@preview/rendercv:{version}": *\n', encoding="utf-8"
        )

        cv = render(
            input_file,
            formats=("typst",),
            design_file=design_file,
            entries_file=entries_file,
        )

        assert '#import "/other/short.typ" as design-file' in (cv.typst or "")
        assert '#import "/other/types.typ" as entries' in (cv.typst or "")

    def test_applies_overrides(self, input_file: pathlib.Path) -> None:
        cv = render(
            input_file, formats=("markdown",), overrides={"cv.name": "John Smith"}
        )

        assert (cv.markdown or "").startswith("# John Smith")

    def test_rejects_unknown_formats(self, input_file: pathlib.Path) -> None:
        with pytest.raises(RenderCVUserError, match=r"Unknown output formats: docx\."):
            render(input_file, formats=("pdf", "docx"))  # ty: ignore[invalid-argument-type]

    def test_raises_validation_errors(self, tmp_path: pathlib.Path) -> None:
        file = tmp_path / "cv.yaml"
        file.write_text("cv:\n  email: nope\n", encoding="utf-8")

        with pytest.raises(RenderCVUserValidationError):
            render(file)


class TestValidate:
    def test_returns_no_problems_for_a_valid_cv(self, input_file: pathlib.Path) -> None:
        assert validate(input_file) == []

    def test_returns_problems_with_their_places(self, tmp_path: pathlib.Path) -> None:
        file = tmp_path / "cv.yaml"
        file.write_text(
            "cv:\n"
            "  name: Jane\n"
            "  sections:\n"
            "    experience:\n"
            "      - compny: ACME\n"
            "        position: Engineer\n",
            encoding="utf-8",
        )

        (problem,) = validate(file)

        assert problem == Problem(
            message=(
                "The entry type `experience` has no field `compny`. Did you mean"
                " `company`?"
            ),
            source="input",
            path=("cv", "sections", "experience", "0", "compny"),
            line=5,
            column=9,
            end_line=5,
            end_column=16,
        )

    def test_reports_typst_errors_without_a_yaml_place(
        self, input_file: pathlib.Path
    ) -> None:
        (input_file.parent / "entries.typ").write_text(
            "#let talk = (\n", encoding="utf-8"
        )

        (problem,) = validate(input_file)

        assert problem.message.startswith(
            "Typst couldn't compile the CV: unclosed delimiter"
        )
        assert "entries.typ`, line 1" in problem.message
        assert (problem.source, problem.path, problem.line) == (None, (), None)

    def test_reports_problems_in_overlays(self, input_file: pathlib.Path) -> None:
        problems = validate(
            input_file, locale_yaml_file="locale:\n  language: englsh\n"
        )

        assert [problem.source for problem in problems] == ["locale"]
        assert "Did you mean `english`?" in problems[0].message


class TestProblemsFromError:
    def test_turns_a_user_error_into_one_problem(self) -> None:
        assert problems_from_error(RenderCVUserError("Broken.")) == [
            Problem(message="Broken.")
        ]

    def test_keeps_validation_errors_without_a_place(self) -> None:
        error = RenderCVUserValidationError(
            [
                RenderCVValidationError(
                    schema_location=None,
                    yaml_location=None,
                    yaml_source="settings_yaml_file",
                    message="Empty.",
                    input="...",
                )
            ]
        )

        assert problems_from_error(error) == [
            Problem(message="Empty.", source="settings")
        ]
