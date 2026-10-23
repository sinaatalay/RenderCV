import pathlib
from datetime import date as Date

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.renderer.path_resolver import (
    resolve_output_folder_placeholder,
    resolve_rendercv_file_path,
)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.render_command import RenderCommand
from rendercv.schema.models.settings.settings import Settings


class TestResolveRendercvFilePath:
    @pytest.mark.parametrize(
        ("file_path_template", "cv_name", "current_date", "expected_filename"),
        [
            # Name placeholders
            ("NAME.pdf", "John Doe", None, "John Doe.pdf"),
            ("NAME_IN_SNAKE_CASE.pdf", "John Doe", None, "John_Doe.pdf"),
            ("NAME_IN_LOWER_SNAKE_CASE.pdf", "John Doe", None, "john_doe.pdf"),
            ("NAME_IN_UPPER_SNAKE_CASE.pdf", "John Doe", None, "JOHN_DOE.pdf"),
            ("NAME_IN_KEBAB_CASE.pdf", "John Doe", None, "John-Doe.pdf"),
            ("NAME_IN_LOWER_KEBAB_CASE.pdf", "John Doe", None, "john-doe.pdf"),
            ("NAME_IN_UPPER_KEBAB_CASE.pdf", "John Doe", None, "JOHN-DOE.pdf"),
            # Date placeholders
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 3, 15), "March.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "Mar.pdf",
            ),
            ("MONTH.pdf", "John Doe", Date(2024, 3, 15), "3.pdf"),
            (
                "MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "03.pdf",
            ),
            ("YEAR.pdf", "John Doe", Date(2024, 3, 15), "2024.pdf"),
            (
                "YEAR_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "24.pdf",
            ),
            # Different months
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 1, 1), "January.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 1, 1),
                "Jan.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 6, 1), "June.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 6, 1),
                "June.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 12, 1), "December.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 12, 1),
                "Dec.pdf",
            ),
            # Day placeholders
            ("DAY.pdf", "John Doe", Date(2024, 3, 15), "15.pdf"),
            ("DAY_IN_TWO_DIGITS.pdf", "John Doe", Date(2024, 3, 5), "05.pdf"),
            # Multiple placeholders
            (
                "NAME_IN_SNAKE_CASE_CV_YEAR-MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "John_Doe_CV_2024-03.pdf",
            ),
            # No placeholders
            ("my_cv.pdf", "John Doe", None, "my_cv.pdf"),
        ],
    )
    def test_resolve_rendercv_file_path(
        self,
        tmp_path: pathlib.Path,
        file_path_template: str,
        cv_name: str,
        current_date: Date | None,
        expected_filename: str,
    ):
        if current_date is not None:
            model = RenderCVModel(
                cv=Cv(name=cv_name), settings=Settings(current_date=current_date)
            )
        else:
            model = RenderCVModel(cv=Cv(name=cv_name))

        file_path = tmp_path / file_path_template
        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == expected_filename
        assert result.parent == tmp_path

    @pytest.mark.parametrize(
        ("cv_name", "expected_filename"),
        [
            ("AC/DC", "AC_DC_CV.pdf"),
            ("../../evil", ".._.._evil_CV.pdf"),
            ('Jane: "J" <Doe>', "Jane___J___Doe__CV.pdf"),
        ],
    )
    def test_keeps_values_in_the_file_name(
        self, tmp_path: pathlib.Path, cv_name: str, expected_filename: str
    ):
        model = RenderCVModel(cv=Cv(name=cv_name))

        result = resolve_rendercv_file_path(
            model, tmp_path / "NAME_IN_SNAKE_CASE_CV.pdf"
        )

        assert result.name == expected_filename
        assert result.parent == tmp_path

    def test_creates_parent_directories(self, tmp_path: pathlib.Path):
        model = RenderCVModel(cv=Cv(name="John Doe"))
        nested_dir = tmp_path / "output" / "cv" / "final"
        file_path = nested_dir / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.parent.exists()
        assert result == nested_dir / "John_Doe_CV.pdf"

    def test_output_folder_placeholder_resolved(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "rendercv_output"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result == output_folder / "John_Doe_CV.pdf"
        assert result.parent.exists()

    def test_custom_output_folder(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build" / "en"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result == output_folder / "John_Doe_CV.pdf"

    def test_no_output_folder_placeholder_in_path(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "custom_dir" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result == tmp_path / "custom_dir" / "John_Doe_CV.pdf"

    def test_output_folder_with_subdirectory_in_path(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "typst" / "NAME_IN_SNAKE_CASE_CV.typ"

        result = resolve_rendercv_file_path(model, file_path)

        assert result == output_folder / "typst" / "John_Doe_CV.typ"


class TestResolveOutputFolderPlaceholder:
    def test_replaces_output_folder_component(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "my_output"
        file_path = tmp_path / "OUTPUT_FOLDER" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder / "file.pdf"

    def test_no_placeholder_returns_unchanged(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "my_output"
        file_path = tmp_path / "some_dir" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == file_path

    def test_nested_output_folder(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build" / "en"
        file_path = tmp_path / "OUTPUT_FOLDER" / "sub" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder / "sub" / "file.pdf"

    def test_output_folder_only(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        file_path = tmp_path / "OUTPUT_FOLDER"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder

    @settings(deadline=None)
    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_idempotent(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        first = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        second = resolve_output_folder_placeholder(first, pathlib.Path(output_folder))
        assert first == second

    @settings(deadline=None)
    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_output_folder_absent_in_result(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        result = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        assert "OUTPUT_FOLDER" not in result.parts
