from collections.abc import Callable

import pytest
from click.testing import Result
from typer.testing import CliRunner

from rendercv.cli.app import app

type RunCli = Callable[..., Result]


@pytest.fixture
def run_cli(monkeypatch: pytest.MonkeyPatch) -> RunCli:
    """Invoke `rendercv` with arguments, like on the command line.

    Why:
        The new-version check would reach PyPI, and Rich wraps long lines at 80
        columns, which splits the messages tests look for.
    """
    monkeypatch.setattr(
        "rendercv.cli.app.warn_if_new_version_is_available", lambda: None
    )
    monkeypatch.setenv("COLUMNS", "500")
    runner = CliRunner()

    def run(*arguments: str) -> Result:
        return runner.invoke(app, list(arguments))

    return run
