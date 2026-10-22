import pathlib

import pydantic
import pytest

from rendercv.schema.models.path import (
    ExistingPathRelativeToInput,
    PlannedPathRelativeToInput,
    serialize_path,
)
from rendercv.schema.models.validation_context import ValidationContext

type Context = dict[str, ValidationContext]


class PlannedPathModel(pydantic.BaseModel):
    output: PlannedPathRelativeToInput


existing_path_adapter = pydantic.TypeAdapter[pathlib.Path](ExistingPathRelativeToInput)
planned_path_adapter = pydantic.TypeAdapter[pathlib.Path](PlannedPathRelativeToInput)
both_adapters = pytest.mark.parametrize(
    "path_adapter", [existing_path_adapter, planned_path_adapter]
)


@pytest.fixture
def existing_file(tmp_path: pathlib.Path) -> pathlib.Path:
    existing = tmp_path / "existing.txt"
    existing.touch()
    return existing


@pytest.fixture
def context(tmp_path: pathlib.Path) -> Context:
    return {"context": ValidationContext(input_file_path=tmp_path / "input.yaml")}


class TestExistingPathRelativeToInput:
    @pytest.mark.parametrize(
        "relative_path",
        ["existing.txt", "subdir/file.txt", "../sibling/file.txt", "./same/file.txt"],
    )
    def test_resolves_relative_paths_to_the_input_folder(
        self, tmp_path: pathlib.Path, context: Context, relative_path: str
    ) -> None:
        expected_path = tmp_path / relative_path
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.touch()

        result = existing_path_adapter.validate_python(relative_path, context=context)

        assert result == expected_path

    def test_keeps_absolute_paths(
        self, existing_file: pathlib.Path, context: Context
    ) -> None:
        assert (
            existing_path_adapter.validate_python(existing_file, context=context)
            == existing_file
        )

    def test_resolves_relative_to_the_current_folder_without_an_input_file(
        self,
        tmp_path: pathlib.Path,
        existing_file: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)

        assert existing_path_adapter.validate_python("existing.txt") == existing_file

    @pytest.mark.parametrize(
        ("path", "expected_message"),
        [
            ("missing.txt", "The file `missing.txt` does not exist."),
            ("sub/missing.txt", "The file `sub/missing.txt` does not exist."),
            (
                "/nonexistent/photo.jpg",
                "The file `/nonexistent/photo.jpg` does not exist.",
            ),
        ],
    )
    def test_rejects_missing_files(
        self, context: Context, path: str, expected_message: str
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            existing_path_adapter.validate_python(path, context=context)

        assert exc_info.value.errors()[0]["msg"] == expected_message

    def test_rejects_folders(self, tmp_path: pathlib.Path, context: Context) -> None:
        (tmp_path / "folder").mkdir()

        with pytest.raises(pydantic.ValidationError) as exc_info:
            existing_path_adapter.validate_python("folder", context=context)

        assert exc_info.value.errors()[0]["msg"] == "The path `folder` is not a file."


class TestPlannedPathRelativeToInput:
    @pytest.mark.parametrize(
        "relative_path",
        ["planned.pdf", "output/result.pdf", "../build/output.html"],
    )
    def test_accepts_files_that_do_not_exist_yet(
        self, tmp_path: pathlib.Path, context: Context, relative_path: str
    ) -> None:
        result = planned_path_adapter.validate_python(relative_path, context=context)

        assert result == tmp_path / relative_path
        assert not result.exists()

    @both_adapters
    def test_results_are_absolute(
        self,
        existing_file: pathlib.Path,
        context: Context,
        path_adapter: pydantic.TypeAdapter[pathlib.Path],
    ) -> None:
        result = path_adapter.validate_python(existing_file.name, context=context)

        assert result.is_absolute()
        assert result == existing_file

    def test_serializes_relative_to_the_current_folder(self) -> None:
        model = PlannedPathModel.model_validate(
            {"output": "build/output.pdf"},
            context={
                "context": ValidationContext(
                    input_file_path=pathlib.Path.cwd() / "input.yaml"
                )
            },
        )

        assert model.model_dump() == {"output": "build/output.pdf"}

    def test_serializes_paths_outside_the_current_folder_as_absolute(
        self, tmp_path: pathlib.Path, context: Context
    ) -> None:
        model = PlannedPathModel.model_validate(
            {"output": tmp_path / "build" / "output.pdf"}, context=context
        )

        assert model.model_dump() == {"output": str(tmp_path / "build" / "output.pdf")}


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (pathlib.Path.cwd() / "a" / "b.pdf", "a/b.pdf"),
        (pathlib.Path("/elsewhere/b.pdf"), "/elsewhere/b.pdf"),
    ],
)
def test_serialize_path(path: pathlib.Path, expected: str) -> None:
    assert serialize_path(path) == expected
