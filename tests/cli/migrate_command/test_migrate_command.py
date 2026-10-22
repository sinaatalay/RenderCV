import pathlib
import shutil
from collections.abc import Callable

import pytest
import ruamel.yaml
from click.testing import Result

from rendercv.cli.migrate_command.migrate_command import (
    load_yaml_mapping,
    plain_yaml_data,
    remove_yaml_key,
    remove_yaml_keys,
)
from rendercv.exception import RenderCVUserError

type RunCli = Callable[..., Result]

cv_part = """# My CV, written for RenderCV 2.
cv:
  name: John Doe  # my name
  sections:
    experience:
      - company: ACME
        position: Engineer
        start_date: 2020-01
        end_date: present
        highlights:
          - A highlight that is long enough that a YAML dumper with the default width would wrap it.
"""
design_part = """design:
  theme: moderncv
  # The page:
  page:
    size: a4
    show_footer: false
  colors:
    name: rgb(0, 0, 0)
  templates:
    one_line_entry:
      main_column: '**LABEL:** DETAILS'
"""
rest_part = """# The language:
locale:
  language: english
settings:
  current_date: 2024-01-01
"""
v2_yaml = cv_part + design_part + rest_part


@pytest.fixture
def v2_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "cv.yaml"
    path.write_text(v2_yaml, encoding="utf-8")
    return path


class TestCliCommandMigrate:
    def test_moves_design_into_design_typ(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 0, result.output
        design = (v2_file.parent / "design.typ").read_text(encoding="utf-8")
        assert '#import "@preview/rendercv:' in design
        assert "#let design = designs.moderncv(" in design
        assert 'size: "a4"' in design
        assert "show_footer: false" in design
        assert "name: rgb(0, 0, 0)" in design

    def test_removes_only_design_from_yaml(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        run_cli("migrate", "cv.yaml")

        # Comments, indentation, and long lines are kept as they are:
        assert v2_file.read_text(encoding="utf-8") == cv_part + rest_part

    def test_keeps_original_as_backup(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        result = run_cli("migrate", "cv.yaml")

        backup = v2_file.parent / "cv.v2.yaml"
        assert backup.read_text(encoding="utf-8") == v2_yaml
        assert "cv.v2.yaml" in result.output

    def test_warns_about_what_it_cannot_convert(
        self,
        run_cli: RunCli,
        v2_file: pathlib.Path,  # noqa: ARG002
    ) -> None:
        result = run_cli("migrate", "cv.yaml")

        assert "Couldn't convert" in result.output
        assert "design.templates.one_line_entry" in result.output

    def test_migrates_design_from_file_in_settings(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        design_file = v2_file.parent / "my_design.yaml"
        design_file.write_text(design_part, encoding="utf-8")
        v2_file.write_text(
            cv_part
            + "settings:\n  render_command:\n    design: my_design.yaml\n"
            + "    pdf_path: cv.pdf\n",
            encoding="utf-8",
        )

        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 0, result.output
        design = (v2_file.parent / "design.typ").read_text(encoding="utf-8")
        assert "designs.moderncv(" in design
        assert v2_file.read_text(encoding="utf-8") == (
            cv_part + "settings:\n  render_command:\n    pdf_path: cv.pdf\n"
        )
        assert design_file.read_text(encoding="utf-8") == design_part

    def test_design_file_in_settings_overrides_design_field(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        (v2_file.parent / "my_design.yaml").write_text(
            "design:\n  theme: sb2nov\n", encoding="utf-8"
        )
        v2_file.write_text(
            v2_yaml + "  render_command:\n    design: my_design.yaml\n",
            encoding="utf-8",
        )

        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 0, result.output
        design = (v2_file.parent / "design.typ").read_text(encoding="utf-8")
        assert "designs.sb2nov(" in design
        assert v2_file.read_text(encoding="utf-8") == (
            cv_part + rest_part + "  render_command:\n"
        )

    def test_migrates_empty_design_field_to_classic(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        v2_file.write_text(cv_part + "design:\n" + rest_part, encoding="utf-8")

        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 0, result.output
        design = (v2_file.parent / "design.typ").read_text(encoding="utf-8")
        assert "#let design = designs.classic()" in design
        assert v2_file.read_text(encoding="utf-8") == cv_part + rest_part

    def test_refuses_to_overwrite_design_typ(
        self, run_cli: RunCli, v2_file: pathlib.Path
    ) -> None:
        design_typ = v2_file.parent / "design.typ"
        design_typ.write_text("// mine", encoding="utf-8")

        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 1
        assert "already exists" in result.output
        assert design_typ.read_text(encoding="utf-8") == "// mine"
        assert v2_file.read_text(encoding="utf-8") == v2_yaml
        assert not (v2_file.parent / "cv.v2.yaml").exists()

    @pytest.mark.parametrize(
        ("contents", "expected_message"),
        [
            (cv_part, "no `design` field"),
            ("", "no `design` field"),
            ("- a list\n", "no `design` field"),
            ("cv: [unclosed\n", "not a valid YAML file"),
            (
                cv_part + "settings:\n  render_command:\n    design: missing.yaml\n",
                "`missing.yaml` doesn't exist",
            ),
        ],
    )
    def test_reports_files_it_cannot_migrate(
        self,
        run_cli: RunCli,
        v2_file: pathlib.Path,
        contents: str,
        expected_message: str,
    ) -> None:
        v2_file.write_text(contents, encoding="utf-8")

        result = run_cli("migrate", "cv.yaml")

        assert result.exit_code == 1
        assert expected_message in result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)
        assert not (v2_file.parent / "design.typ").exists()

    def test_reports_missing_file(
        self, run_cli: RunCli, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)

        result = run_cli("migrate", "missing.yaml")

        assert result.exit_code == 1
        assert "`missing.yaml` doesn't exist" in result.output

    @pytest.mark.parametrize("version_two_yaml", ["small", "example"])
    def test_migrated_project_renders(
        self,
        run_cli: RunCli,
        v2_file: pathlib.Path,
        testdata_dir: pathlib.Path,
        version_two_yaml: str,
    ) -> None:
        if version_two_yaml == "example":
            shutil.copyfile(testdata_dir / "John_Doe_CV.yaml", v2_file)

        migrate_result = run_cli("migrate", "cv.yaml")
        render_result = run_cli("render", "cv.yaml", "-nopng", "-nohtml", "-nomd")

        assert migrate_result.exit_code == 0, migrate_result.output
        assert render_result.exit_code == 0, render_result.output
        assert (v2_file.parent / "rendercv_output" / "John_Doe_CV.pdf").is_file()


def test_load_yaml_mapping() -> None:
    yaml = ruamel.yaml.YAML()

    assert load_yaml_mapping(yaml, "a: 1\n", pathlib.Path("x.yaml")) == {"a": 1}
    assert load_yaml_mapping(yaml, "- 1\n", pathlib.Path("x.yaml")) == {}
    with pytest.raises(RenderCVUserError, match=r"`x\.yaml` is not a valid YAML"):
        load_yaml_mapping(yaml, "a: [\n", pathlib.Path("x.yaml"))


@pytest.mark.parametrize(
    ("source", "line", "expected"),
    [
        # A top-level key in the middle, with comments of its own:
        (
            "a: 1\nb:\n  c: 2\n  # about c\n\n  d: 3\ne: 4\n",
            1,
            "a: 1\ne: 4\n",
        ),
        # A comment at the key's indentation belongs to the next key:
        ("a:\n  b: 1\n# about c\nc: 2\n", 0, "# about c\nc: 2\n"),
        # The last key:
        ("a: 1\nb:\n  - 1\n  - 2\n", 1, "a: 1\n"),
        # A nested key:
        (
            "s:\n  r:\n    design: d.yaml\n    pdf: x\n",
            2,
            "s:\n  r:\n    pdf: x\n",
        ),
    ],
)
def test_remove_yaml_key(source: str, line: int, expected: str) -> None:
    assert remove_yaml_key(source, line) == expected


class TestRemoveYamlKeys:
    def test_edits_block_style_yaml_line_by_line(self) -> None:
        yaml = ruamel.yaml.YAML()
        source = "# top\na:\n    - 1   # one\nb: 2\nc:\n  d: 3\n  e: 4\n"
        document = yaml.load(source)

        result = remove_yaml_keys(
            yaml, source, document, [(document, "b"), (document["c"], "d")]
        )

        assert result == "# top\na:\n    - 1   # one\nc:\n  e: 4\n"

    def test_dumps_yaml_again_when_it_cannot_edit_lines(self) -> None:
        yaml = ruamel.yaml.YAML()
        source = "{cv: {name: John}, design: {theme: classic}}\n"
        document = yaml.load(source)

        result = remove_yaml_keys(yaml, source, document, [(document, "design")])

        assert yaml.load(result) == {"cv": {"name": "John"}}


def test_plain_yaml_data() -> None:
    yaml = ruamel.yaml.YAML()
    source = "a: !typst $x$\nb: [1, 2.5, 2024-01-01]\n"

    assert plain_yaml_data(yaml.load(source)) == plain_yaml_data(yaml.load(source))
    assert plain_yaml_data(yaml.load(source)) != plain_yaml_data(
        yaml.load("a: $x$\nb: [1, 2.5, 2024-01-01]\n")
    )
