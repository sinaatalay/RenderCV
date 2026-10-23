import pathlib
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rendercv import __version__
from rendercv.cli.app import app


def test_all_commands_are_registered():
    cli_folder = (
        pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv" / "cli"
    )
    command_files = list(cli_folder.rglob("*_command.py"))

    registered_commands = app.registered_commands

    assert len(registered_commands) == len(command_files)


class TestCliCommandNoArgs:
    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_prints_version_when_requested(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output
        mock_warn.assert_called_once()

    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_prints_version_with_short_flag(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output
        mock_warn.assert_called_once()

    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_shows_help_when_no_args(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "RenderCV is a command-line tool" in result.output
        mock_warn.assert_called_once()


@pytest.mark.parametrize("quiet", ["--quiet", "-q"])
@pytest.mark.parametrize(
    ("command", "argument", "filename"),
    [
        ("new", "John Doe", "John_Doe_CV.yaml"),
        ("create-theme", "mytheme", "mytheme/__init__.py"),
    ],
)
def test_creation_commands_support_quiet(
    tmp_path, monkeypatch, quiet, command, argument, filename
):
    monkeypatch.chdir(tmp_path)
    with patch("rendercv.cli.error_handler.warn_if_new_version_is_available") as warn:
        result = CliRunner().invoke(app, [command, argument, quiet])
    assert result.exit_code == 0, result.output
    assert result.output == ""
    assert (tmp_path / filename).is_file()
    warn.assert_not_called()


@pytest.mark.parametrize(
    ("command", "argument"), [("new", "John"), ("create-theme", "INVALID")]
)
def test_quiet_creation_errors(tmp_path, monkeypatch, command, argument):
    monkeypatch.chdir(tmp_path)
    args = [command, argument, "-q"]
    if command == "new":
        args.extend(["--theme", "INVALID"])
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 1
    assert result.output == ""
