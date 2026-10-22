import pathlib
import runpy
import shutil
from collections.abc import Callable

import pytest

repository_root = pathlib.Path(__file__).parent.parent.parent

type RunScript = Callable[..., None]


@pytest.fixture
def run_script(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> RunScript:
    """Run a script of `scripts/` as if `tmp_path` were the repository.

    Why:
        The scripts write into the repository (`schema.json`, `examples/`,
        `docs/`). Running a copy of a script from `tmp_path/scripts/` makes it
        write into `tmp_path` instead.
    """

    def run(script_name: str, *files_it_reads: str) -> None:
        (tmp_path / "scripts").mkdir(exist_ok=True)
        script_path = tmp_path / "scripts" / script_name
        shutil.copyfile(repository_root / "scripts" / script_name, script_path)
        for file in files_it_reads:
            (tmp_path / file).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repository_root / file, tmp_path / file)
        monkeypatch.chdir(tmp_path)
        runpy.run_path(str(script_path), run_name="__main__")

    return run


@pytest.fixture
def two_designs(monkeypatch: pytest.MonkeyPatch) -> tuple[str, ...]:
    """Make the scripts render two built-in designs instead of all, to be fast."""
    designs = ("classic", "moderncv")
    monkeypatch.setattr(
        "rendercv.schema.sample_generator.get_built_in_design_names", lambda: designs
    )
    return designs
