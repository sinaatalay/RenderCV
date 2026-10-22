import pathlib
from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from click.testing import Result

from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.sample_generator import create_sample_entries_file

type RunCli = Callable[..., Result]

cv_yaml = """cv:
  name: John Doe
  email: john@example.com
  sections:
    experience:
      - company: ACME
        position: Engineer
        start_date: 2020-01
        end_date: present
        highlights:
          - Built things.
    skills:
      - label: Languages
        details: Python, Typst
"""
# Valid only with the `talk` entry type of the sample `entries.typ`:
talk_cv_yaml = """cv:
  name: John Doe
  sections:
    talks:
      - title: Typst for CVs
        event: TypstConf
        date: 2024-05
"""
a4_design = (
    f'#import "@preview/rendercv:{get_rendercv_typst_version()}": designs\n'
    '#let design = designs.classic(page: (size: "a4"))\n'
)
all_outputs = [
    "John_Doe_CV.typ",
    "John_Doe_CV.pdf",
    "John_Doe_CV_1.png",
    "John_Doe_CV.md",
    "John_Doe_CV.html",
]


def is_a4(png_path: pathlib.Path) -> bool:
    # A PNG's width and height are bytes 16-24; A4 is taller than US Letter:
    header = png_path.read_bytes()[16:24]
    width, height = int.from_bytes(header[:4]), int.from_bytes(header[4:])
    return round(height / width, 2) == 1.41


@pytest.fixture
def cv_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "John_Doe_CV.yaml"
    path.write_text(cv_yaml, encoding="utf-8")
    return path


@pytest.fixture
def cv_file_in_folder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> pathlib.Path:
    # The YAML file is in `cv/`, and the current folder is its parent:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cv").mkdir()
    path = tmp_path / "cv" / "John_Doe_CV.yaml"
    path.write_text(talk_cv_yaml, encoding="utf-8")
    return path


class TestCliCommandRender:
    def test_generates_every_output(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        result = run_cli("render", "John_Doe_CV.yaml")

        assert result.exit_code == 0, result.output
        assert "Your CV is ready" in result.output
        for name in all_outputs:
            assert (cv_file.parent / "rendercv_output" / name).is_file()

    @pytest.mark.parametrize(
        ("flag", "skipped_output"),
        [
            ("--dont-generate-typst", "John_Doe_CV.typ"),
            ("-notyp", "John_Doe_CV.typ"),
            ("--dont-generate-pdf", "John_Doe_CV.pdf"),
            ("-nopdf", "John_Doe_CV.pdf"),
            ("--dont-generate-png", "John_Doe_CV_1.png"),
            ("-nopng", "John_Doe_CV_1.png"),
            ("--dont-generate-markdown", "John_Doe_CV.md"),
            ("-nomd", "John_Doe_CV.md"),
            ("--dont-generate-html", "John_Doe_CV.html"),
            ("-nohtml", "John_Doe_CV.html"),
        ],
    )
    def test_skips_outputs_that_are_turned_off(
        self, run_cli: RunCli, cv_file: pathlib.Path, flag: str, skipped_output: str
    ) -> None:
        result = run_cli("render", "John_Doe_CV.yaml", flag)

        assert result.exit_code == 0, result.output
        output_folder = cv_file.parent / "rendercv_output"
        assert not (output_folder / skipped_output).exists()
        for name in all_outputs:
            if name != skipped_output:
                assert (output_folder / name).is_file()

    def test_prints_nothing_when_quiet(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        result = run_cli("render", "John_Doe_CV.yaml", "--quiet", "-nopng")

        assert result.exit_code == 0, result.output
        assert result.output == ""
        assert (cv_file.parent / "rendercv_output" / "John_Doe_CV.pdf").is_file()

    def test_writes_outputs_to_paths_relative_to_input_file(
        self, run_cli: RunCli, cv_file_in_folder: pathlib.Path
    ) -> None:
        cv_file_in_folder.write_text(cv_yaml, encoding="utf-8")

        result = run_cli(
            "render",
            "cv/John_Doe_CV.yaml",
            "--output-folder",
            "out",
            "--pdf-path",
            "my.pdf",
            "--png-path",
            "images/page.png",
            "--typst-path",
            "OUTPUT_FOLDER/source.typ",
            "--markdown-path",
            "my.md",
            "--html-path",
            "my.html",
        )

        assert result.exit_code == 0, result.output
        cv_folder = cv_file_in_folder.parent
        for path in ["my.pdf", "images/page_1.png", "out/source.typ", "my.md"]:
            assert (cv_folder / path).is_file()
        assert (cv_folder / "my.html").is_file()

    def test_overrides_yaml_fields_from_command_line(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        result = run_cli(
            "render", "John_Doe_CV.yaml", "--cv.name", "Jane Doe", "-nopng"
        )

        assert result.exit_code == 0, result.output
        assert (cv_file.parent / "rendercv_output" / "Jane_Doe_CV.pdf").is_file()
        assert "Jane Doe" in (
            cv_file.parent / "rendercv_output" / "Jane_Doe_CV.md"
        ).read_text(encoding="utf-8")

    def test_rejects_override_without_value(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        result = run_cli("render", cv_file.name, "--cv.name")

        assert result.exit_code == 1
        assert "Each key should have a corresponding value" in result.output

    @pytest.mark.parametrize(
        ("option", "overlay", "expected_in_typst"),
        [
            ("--locale-catalog", "locale:\n  language: turkish\n", '"Ocak"'),
            ("-lc", "locale:\n  language: turkish\n", '"Ocak"'),
            ("--settings", "settings:\n  current_date: 1999-01-15\n", '"year": 1999'),
            ("-s", "settings:\n  current_date: 1999-01-15\n", '"year": 1999'),
        ],
    )
    def test_reads_overlay_files(
        self,
        run_cli: RunCli,
        cv_file: pathlib.Path,
        option: str,
        overlay: str,
        expected_in_typst: str,
    ) -> None:
        (cv_file.parent / "overlay.yaml").write_text(overlay, encoding="utf-8")

        result = run_cli("render", cv_file.name, option, "overlay.yaml", "-nopng")

        assert result.exit_code == 0, result.output
        typst_source = (
            cv_file.parent / "rendercv_output" / "John_Doe_CV.typ"
        ).read_text(encoding="utf-8")
        assert expected_in_typst in typst_source

    def test_uses_design_and_entries_given_relative_to_current_folder(
        self, run_cli: RunCli, cv_file_in_folder: pathlib.Path
    ) -> None:
        styles = cv_file_in_folder.parent.parent / "styles"
        styles.mkdir()
        (styles / "a4.typ").write_text(a4_design, encoding="utf-8")
        (styles / "talks.typ").write_text(
            create_sample_entries_file(), encoding="utf-8"
        )

        result = run_cli(
            "render",
            "cv/John_Doe_CV.yaml",
            "--design",
            "styles/a4.typ",
            "--entries",
            "styles/talks.typ",
        )

        assert result.exit_code == 0, result.output
        output_folder = cv_file_in_folder.parent / "rendercv_output"
        assert is_a4(output_folder / "John_Doe_CV_1.png")

    def test_uses_design_and_entries_next_to_input_file(
        self, run_cli: RunCli, cv_file_in_folder: pathlib.Path
    ) -> None:
        cv_folder = cv_file_in_folder.parent
        (cv_folder / "design.typ").write_text(a4_design, encoding="utf-8")
        (cv_folder / "entries.typ").write_text(
            create_sample_entries_file(), encoding="utf-8"
        )

        result = run_cli("render", "cv/John_Doe_CV.yaml")

        assert result.exit_code == 0, result.output
        assert is_a4(cv_folder / "rendercv_output" / "John_Doe_CV_1.png")

    def test_uses_design_and_entries_from_settings_relative_to_input_file(
        self, run_cli: RunCli, cv_file_in_folder: pathlib.Path
    ) -> None:
        cv_folder = cv_file_in_folder.parent
        (cv_folder / "styles").mkdir()
        (cv_folder / "styles" / "a4.typ").write_text(a4_design, encoding="utf-8")
        (cv_folder / "styles" / "talks.typ").write_text(
            create_sample_entries_file(), encoding="utf-8"
        )
        cv_file_in_folder.write_text(
            talk_cv_yaml
            + "settings:\n  render_command:\n    design: styles/a4.typ\n"
            + "    entries: styles/talks.typ\n",
            encoding="utf-8",
        )

        result = run_cli("render", "cv/John_Doe_CV.yaml")

        assert result.exit_code == 0, result.output
        assert is_a4(cv_folder / "rendercv_output" / "John_Doe_CV_1.png")

    def test_command_line_design_overrides_design_next_to_input_file(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        (cv_file.parent / "design.typ").write_text("#let design = (", encoding="utf-8")
        (cv_file.parent / "a4.typ").write_text(a4_design, encoding="utf-8")

        result = run_cli("render", cv_file.name, "--design", "a4.typ")

        assert result.exit_code == 0, result.output
        assert is_a4(cv_file.parent / "rendercv_output" / "John_Doe_CV_1.png")

    @pytest.mark.parametrize("option", ["--design", "-d", "--entries", "-e"])
    def test_rejects_design_or_entries_that_are_not_typst_files(
        self, run_cli: RunCli, cv_file: pathlib.Path, option: str
    ) -> None:
        (cv_file.parent / "old.yaml").write_text(
            "design:\n  theme: classic\n", encoding="utf-8"
        )

        result = run_cli("render", cv_file.name, option, "old.yaml")

        assert result.exit_code == 1
        assert "should be a Typst file (`.typ`)" in result.output
        assert "rendercv migrate" in result.output

    def test_rejects_missing_design_file(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        result = run_cli("render", cv_file.name, "--design", "missing.typ")

        assert result.exit_code == 1
        assert "`missing.typ` doesn't exist" in result.output

    def test_rejects_design_in_settings_that_is_not_typst_file(
        self, run_cli: RunCli, cv_file: pathlib.Path
    ) -> None:
        (cv_file.parent / "old.yaml").write_text(
            "design:\n  theme: classic\n", encoding="utf-8"
        )
        cv_file.write_text(
            cv_yaml + "settings:\n  render_command:\n    design: old.yaml\n",
            encoding="utf-8",
        )

        result = run_cli("render", cv_file.name)

        assert result.exit_code == 1
        assert "settings.render_command.design" in result.output
        assert "line 17" in result.output
        assert "Typst file" in result.output

    @pytest.mark.parametrize(
        ("contents", "expected_messages"),
        [
            (
                cv_yaml.replace("john@example.com", "not-an-email"),
                ["cv.email", "(line 3)", "not-an-email"],
            ),
            (
                cv_yaml + "design:\n  theme: classic\n",
                ["design", "(lines 15-16)", "rendercv migrate"],
            ),
            ("cv:\n  name: [John\n", ["not a valid YAML file", "line"]),
        ],
    )
    def test_prints_validation_errors_with_line_numbers(
        self,
        run_cli: RunCli,
        cv_file: pathlib.Path,
        contents: str,
        expected_messages: list[str],
    ) -> None:
        cv_file.write_text(contents, encoding="utf-8")

        result = run_cli("render", cv_file.name)

        assert result.exit_code == 1
        assert "There are validation errors!" in result.output
        for message in expected_messages:
            assert message in result.output
        assert not (cv_file.parent / "rendercv_output" / "John_Doe_CV.pdf").exists()

    @pytest.mark.parametrize(
        ("design", "expected_message"),
        [
            ("#let design = (", "unclosed delimiter"),
            (
                a4_design.replace('"a4"', "12"),
                "Design option `page.size` should be of type string",
            ),
            ("#let x = 1", "The design file must define `design`"),
        ],
    )
    def test_prints_typst_errors(
        self,
        run_cli: RunCli,
        cv_file: pathlib.Path,
        design: str,
        expected_message: str,
    ) -> None:
        (cv_file.parent / "design.typ").write_text(design, encoding="utf-8")

        result = run_cli("render", cv_file.name)

        assert result.exit_code == 1
        assert "Typst couldn't compile the CV" in result.output
        assert expected_message in result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)

    def test_rejects_missing_input_file(
        self, run_cli: RunCli, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)

        result = run_cli("render", "missing.yaml")

        assert result.exit_code == 1
        assert "The input file `missing.yaml` doesn't exist." in result.output

    def test_watches_every_input_file(
        self,
        run_cli: RunCli,
        cv_file: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (cv_file.parent / "design.typ").write_text(a4_design, encoding="utf-8")
        (cv_file.parent / "settings.yaml").write_text(
            "settings:\n  current_date: 2024-01-01\n", encoding="utf-8"
        )
        watcher = MagicMock()
        monkeypatch.setattr(
            "rendercv.cli.render_command.render_command.run_function_if_files_change",
            watcher,
        )

        result = run_cli(
            "render", cv_file.name, "--watch", "--settings", "settings.yaml"
        )

        assert result.exit_code == 0, result.output
        file_paths, function = watcher.call_args.args
        assert set(file_paths()) == {
            cv_file,
            cv_file.parent / "design.typ",
            cv_file.parent / "settings.yaml",
        }
        # The watcher renders with the same options:
        function()
        assert is_a4(cv_file.parent / "rendercv_output" / "John_Doe_CV_1.png")
