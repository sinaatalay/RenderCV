import pathlib
from collections.abc import Callable

import pytest
from click.testing import Result

from rendercv.cli.new_command.new_command import (
    build_creation_panel,
    built_in_design_names,
)
from rendercv.schema.sample_generator import get_built_in_design_names

type RunCli = Callable[..., Result]


@pytest.fixture
def project_folder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> pathlib.Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestCliCommandNew:
    @pytest.mark.parametrize(
        ("options", "expected_files"),
        [
            ([], {"John_Doe_CV.yaml"}),
            (["--design", "moderncv"], {"John_Doe_CV.yaml", "design.typ"}),
            (["--entries"], {"John_Doe_CV.yaml", "entries.typ"}),
            (
                ["--design", "sb2nov", "--entries"],
                {"John_Doe_CV.yaml", "design.typ", "entries.typ"},
            ),
        ],
    )
    def test_creates_files(
        self,
        run_cli: RunCli,
        project_folder: pathlib.Path,
        options: list[str],
        expected_files: set[str],
    ) -> None:
        result = run_cli("new", "John Doe", *options)

        assert result.exit_code == 0, result.output
        assert {path.name for path in project_folder.iterdir()} == expected_files
        assert "Welcome to" in result.output
        assert "Created your YAML input file: ./John_Doe_CV.yaml" in result.output

    def test_design_file_uses_chosen_design(
        self, run_cli: RunCli, project_folder: pathlib.Path
    ) -> None:
        run_cli("new", "John Doe", "--design", "moderncv")

        design = (project_folder / "design.typ").read_text(encoding="utf-8")
        assert "#let design = designs.moderncv(" in design

    def test_yaml_file_uses_given_name_and_locale(
        self, run_cli: RunCli, project_folder: pathlib.Path
    ) -> None:
        result = run_cli("new", "Jane Doe", "--locale", "turkish")

        assert result.exit_code == 0, result.output
        yaml = (project_folder / "Jane_Doe_CV.yaml").read_text(encoding="utf-8")
        assert 'name: "Jane Doe"' in yaml
        assert "language: turkish" in yaml

    def test_created_project_renders(
        self, run_cli: RunCli, project_folder: pathlib.Path
    ) -> None:
        new_result = run_cli("new", "John Doe", "--design", "moderncv", "--entries")
        render_result = run_cli("render", "John_Doe_CV.yaml", "-nopng", "-nohtml")

        assert new_result.exit_code == 0, new_result.output
        assert render_result.exit_code == 0, render_result.output
        output_folder = project_folder / "rendercv_output"
        assert (output_folder / "John_Doe_CV.pdf").is_file()
        # The design and entry types next to the YAML file were used:
        typst_source = (output_folder / "John_Doe_CV.typ").read_text(encoding="utf-8")
        assert '#import "/design.typ"' in typst_source
        assert '#import "/entries.typ"' in typst_source

    def test_does_not_overwrite_existing_files(
        self, run_cli: RunCli, project_folder: pathlib.Path
    ) -> None:
        names = ["John_Doe_CV.yaml", "design.typ", "entries.typ"]
        for name in names:
            (project_folder / name).write_text("mine", encoding="utf-8")

        result = run_cli("new", "John Doe", "--design", "classic", "--entries")

        assert result.exit_code == 0, result.output
        for name in names:
            assert (project_folder / name).read_text(encoding="utf-8") == "mine"
        assert "Your YAML input file already exists" in result.output
        assert "Not modified (already exist)" in result.output

    @pytest.mark.parametrize(
        ("options", "expected_message"),
        [
            (["--design", "nonexistent"], "There is no built-in design `nonexistent`"),
            (["--locale", "nonexistent"], "The locale `nonexistent` is not built in"),
        ],
    )
    def test_rejects_unknown_design_or_locale(
        self,
        run_cli: RunCli,
        project_folder: pathlib.Path,
        options: list[str],
        expected_message: str,
    ) -> None:
        result = run_cli("new", "John Doe", *options)

        assert result.exit_code == 1
        assert expected_message in result.output
        assert "moderncv" in result.output or "english" in result.output
        # Nothing is created:
        assert list(project_folder.iterdir()) == []


class TestBuildCreationPanel:
    def test_lists_created_and_existing_files(self) -> None:
        input_file = pathlib.Path("John_Doe_CV.yaml")

        panel = build_creation_panel(
            input_file,
            created_items=[("Your YAML input file", input_file)],
            existing_items=[("Your design", pathlib.Path("design.typ"))],
        )

        text = str(panel.renderable)
        assert "Created your YAML input file: [purple]./John_Doe_CV.yaml" in text
        assert "Not modified (already exist):\n  - Your design: ./design.typ" in text

    def test_omits_design_note_when_only_yaml_file_is_involved(self) -> None:
        input_file = pathlib.Path("John_Doe_CV.yaml")

        panel = build_creation_panel(
            input_file,
            created_items=[("Your YAML input file", input_file)],
            existing_items=[],
        )

        assert "design.typ" not in str(panel.renderable)


def test_built_in_design_names_match_the_typst_package() -> None:
    assert built_in_design_names == get_built_in_design_names()
