import pathlib
import sys

import pytest
import typer

from rendercv.cli.render_command.progress_panel import ProgressPanel
from rendercv.cli.render_command.run_rendercv import (
    collect_input_file_paths,
    run_rendercv,
    timed_step,
)


class RecordingProgressPanel(ProgressPanel):
    """Remembers the steps it showed when rendering finished."""

    def __init__(self, quiet: bool = False) -> None:
        super().__init__(quiet=quiet)
        self.finished_steps: list[str] = []

    def finish_progress(self) -> None:
        self.finished_steps = [step.message for step in self.completed_steps]
        super().finish_progress()


class TestTimedStep:
    def test_returns_function_result(self) -> None:
        def double(x: int) -> int:
            return x * 2

        result = timed_step("Test", ProgressPanel(quiet=True), double, 5)

        assert result == 10

    def test_passes_arguments_to_function(self) -> None:
        def add(a: int, b: int, c: int = 0) -> int:
            return a + b + c

        result = timed_step("Test", ProgressPanel(quiet=True), add, 1, 2, c=3)

        assert result == 6

    def test_shows_no_step_without_paths(self) -> None:
        progress = ProgressPanel(quiet=True)

        timed_step("Test", progress, lambda: None)

        assert progress.completed_steps == []

    def test_shows_step_with_single_path(self) -> None:
        progress = ProgressPanel(quiet=True)
        path = pathlib.Path.cwd() / "output.pdf"

        timed_step("Generated PDF", progress, lambda: path)

        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].message == "Generated PDF"
        assert progress.completed_steps[0].paths == [path]

    def test_pluralizes_message_for_multiple_paths(self) -> None:
        progress = ProgressPanel(quiet=True)
        paths = [pathlib.Path.cwd() / "page_1.png", pathlib.Path.cwd() / "page_2.png"]

        timed_step("Generated PNG", progress, lambda: paths)

        assert progress.completed_steps[0].message == "Generated PNGs"
        assert progress.completed_steps[0].paths == paths


class TestCollectInputFilePaths:
    def test_returns_only_input_file_by_default(self, tmp_path: pathlib.Path) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")

        assert collect_input_file_paths(yaml_file) == {"input": yaml_file}

    def test_includes_design_and_entries_next_to_input_file(
        self, tmp_path: pathlib.Path
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        (tmp_path / "design.typ").touch()
        (tmp_path / "entries.typ").touch()

        assert collect_input_file_paths(yaml_file) == {
            "input": yaml_file,
            "design": tmp_path / "design.typ",
            "entries": tmp_path / "entries.typ",
        }

    def test_includes_files_given_on_command_line(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        for name in ["d.typ", "e.typ", "locale.yaml", "settings.yaml"]:
            (tmp_path / name).touch()

        result = collect_input_file_paths(
            yaml_file,
            design=pathlib.Path("d.typ"),
            entries=pathlib.Path("e.typ"),
            locale=pathlib.Path("locale.yaml"),
            settings=pathlib.Path("settings.yaml"),
        )

        assert result == {
            "input": yaml_file,
            "design": tmp_path / "d.typ",
            "entries": tmp_path / "e.typ",
            "locale": tmp_path / "locale.yaml",
            "settings": tmp_path / "settings.yaml",
        }

    def test_includes_files_from_settings_relative_to_input_file(
        self, tmp_path: pathlib.Path
    ) -> None:
        (tmp_path / "cv").mkdir()
        (tmp_path / "shared").mkdir()
        for name in ["d.typ", "e.typ", "locale.yaml"]:
            (tmp_path / "shared" / name).touch()
        yaml_file = tmp_path / "cv" / "cv.yaml"
        yaml_file.write_text(
            "cv:\n  name: John Doe\nsettings:\n  render_command:\n"
            "    design: ../shared/d.typ\n    entries: ../shared/e.typ\n"
            "    locale: ../shared/locale.yaml\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(yaml_file)

        assert result == {
            "input": yaml_file,
            "design": tmp_path / "cv" / "../shared/d.typ",
            "entries": tmp_path / "cv" / "../shared/e.typ",
            "locale": tmp_path / "cv" / "../shared/locale.yaml",
        }

    def test_command_line_files_take_precedence(self, tmp_path: pathlib.Path) -> None:
        (tmp_path / "design.typ").touch()
        (tmp_path / "from_yaml.typ").touch()
        (tmp_path / "from_cli.typ").touch()
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "settings:\n  render_command:\n    entries: from_yaml.typ\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(
            yaml_file,
            design=tmp_path / "from_cli.typ",
            entries=tmp_path / "from_cli.typ",
        )

        assert result["design"] == tmp_path / "from_cli.typ"
        assert result["entries"] == tmp_path / "from_cli.typ"

    def test_skips_files_that_do_not_exist(self, tmp_path: pathlib.Path) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "settings:\n  render_command:\n    design: missing.typ\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(
            yaml_file, entries=tmp_path / "missing.typ", settings=tmp_path / "x.yaml"
        )

        assert result == {"input": yaml_file}

    @pytest.mark.parametrize(
        "contents",
        [
            "invalid: yaml: content: :",
            "",
            "- a list\n",
            "settings: a string\n",
            "settings:\n  render_command: [a list]\n",
            None,
        ],
    )
    def test_returns_input_file_when_it_is_broken_or_missing(
        self, tmp_path: pathlib.Path, contents: str | None
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        if contents is not None:
            yaml_file.write_text(contents, encoding="utf-8")
        (tmp_path / "design.typ").touch()

        assert collect_input_file_paths(yaml_file) == {
            "input": yaml_file,
            "design": tmp_path / "design.typ",
        }


class TestRunRendercv:
    def test_renders_outputs_and_reports_them(self, tmp_path: pathlib.Path) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        progress = RecordingProgressPanel(quiet=True)

        with progress:
            run_rendercv(yaml_file, progress, dont_generate_png=True)

        assert progress.finished_steps == [
            "Generated Typst",
            "Generated PDF",
            "Generated Markdown",
            "Generated HTML",
        ]
        assert (tmp_path / "rendercv_output" / "John_Doe_CV.pdf").is_file()

    def test_reads_locale_file_from_settings(self, tmp_path: pathlib.Path) -> None:
        (tmp_path / "locale.yaml").write_text(
            "locale:\n  language: turkish\n", encoding="utf-8"
        )
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "cv:\n  name: John Doe\nsettings:\n  render_command:\n"
            "    locale: locale.yaml\n",
            encoding="utf-8",
        )
        progress = ProgressPanel(quiet=True)

        with progress:
            run_rendercv(yaml_file, progress, dont_generate_png=True)

        typst_file = tmp_path / "rendercv_output" / "John_Doe_CV.typ"
        assert '"language": "turkish"' in typst_file.read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("contents", "design"),
        [
            # Invalid YAML:
            ("invalid: yaml: content: :", None),
            # Invalid CV:
            ("cv:\n  email: not-an-email\n", None),
            # Invalid design:
            ("cv:\n  name: John Doe\n", "#let design = ("),
        ],
    )
    def test_exits_with_error_for_invalid_input(
        self, tmp_path: pathlib.Path, contents: str, design: str | None
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(contents, encoding="utf-8")
        if design is not None:
            (tmp_path / "design.typ").write_text(design, encoding="utf-8")
        progress = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info, progress:
            run_rendercv(yaml_file, progress)

        assert exc_info.value.exit_code == 1

    def test_exits_with_error_for_missing_file(self, tmp_path: pathlib.Path) -> None:
        progress = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info, progress:
            run_rendercv(tmp_path / "missing.yaml", progress)

        assert exc_info.value.exit_code == 1

    @pytest.mark.skipif(
        sys.platform == "win32", reason="chmod doesn't work the same on Windows"
    )
    def test_exits_with_error_for_unreadable_file(self, tmp_path: pathlib.Path) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        yaml_file.chmod(0o000)
        progress = ProgressPanel(quiet=True)

        try:
            with pytest.raises(typer.Exit) as exc_info, progress:
                run_rendercv(yaml_file, progress)
        finally:
            yaml_file.chmod(0o644)

        assert exc_info.value.exit_code == 1
