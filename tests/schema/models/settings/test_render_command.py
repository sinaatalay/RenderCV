import pathlib

import pydantic
import pydantic_core
import pytest

from rendercv.schema.models.settings.render_command import (
    RenderCommand,
    check_typst_file,
)
from rendercv.schema.models.validation_context import ValidationContext


@pytest.fixture
def context(tmp_path: pathlib.Path) -> dict[str, ValidationContext]:
    return {"context": ValidationContext(input_file_path=tmp_path / "cv.yaml")}


class TestCheckTypstFile:
    def test_accepts_typst_files(self) -> None:
        path = pathlib.Path("design.typ")

        assert check_typst_file(path) == path

    @pytest.mark.parametrize("name", ["design.yaml", "design.yml", "design"])
    def test_rejects_other_files(self, name: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError, match=r"\(`\.typ`\)"):
            check_typst_file(pathlib.Path(name))


class TestRenderCommand:
    def test_defaults(self) -> None:
        render_command = RenderCommand()

        assert render_command.design is None
        assert render_command.entries is None
        assert render_command.locale is None
        assert render_command.pdf_path.name == "NAME_IN_SNAKE_CASE_CV.pdf"
        assert not render_command.dont_generate_pdf

    def test_resolves_paths_relative_to_the_yaml_file(
        self, tmp_path: pathlib.Path, context: dict[str, ValidationContext]
    ) -> None:
        (tmp_path / "themes").mkdir()
        (tmp_path / "themes" / "design.typ").touch()
        (tmp_path / "entries.typ").touch()
        (tmp_path / "locale.yaml").touch()

        render_command = RenderCommand.model_validate(
            {
                "design": "themes/design.typ",
                "entries": "entries.typ",
                "locale": "locale.yaml",
                "output_folder": "out",
                "pdf_path": "out/cv.pdf",
            },
            context=context,
        )

        assert render_command.design == tmp_path / "themes" / "design.typ"
        assert render_command.entries == tmp_path / "entries.typ"
        assert render_command.locale == tmp_path / "locale.yaml"
        assert render_command.output_folder == tmp_path / "out"
        assert render_command.pdf_path == tmp_path / "out" / "cv.pdf"

    @pytest.mark.parametrize("field", ["design", "entries"])
    def test_rejects_missing_typst_files(
        self, context: dict[str, ValidationContext], field: str
    ) -> None:
        with pytest.raises(pydantic.ValidationError, match="does not exist"):
            RenderCommand.model_validate({field: "missing.typ"}, context=context)

    @pytest.mark.parametrize("field", ["design", "entries"])
    def test_rejects_rendercv_2_yaml_designs(
        self,
        tmp_path: pathlib.Path,
        context: dict[str, ValidationContext],
        field: str,
    ) -> None:
        (tmp_path / "design.yaml").touch()

        with pytest.raises(pydantic.ValidationError, match="should be a Typst file"):
            RenderCommand.model_validate({field: "design.yaml"}, context=context)
