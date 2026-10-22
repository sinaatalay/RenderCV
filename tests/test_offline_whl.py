"""Test that RenderCV's distributions are complete and work without internet.

Why:
    The wheel bundles RenderCV's Typst package and the Typst packages it
    depends on (by `hatch_build.py`), so RenderCV never downloads anything
    while rendering. The source distribution must hold everything needed to
    build that wheel, and nothing else.
"""

import os
import pathlib
import subprocess
import sys
import tarfile
import zipfile
from typing import Any

import pytest

from rendercv.renderer.typst_packages import get_rendercv_typst_version

project_root = pathlib.Path(__file__).parent.parent


def run(arguments: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Run a command and fail with its output if it fails."""
    result = subprocess.run(
        arguments, capture_output=True, text=True, timeout=300, check=False, **kwargs
    )
    if result.returncode != 0:
        message = (
            f"Command {arguments} failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
        raise AssertionError(message)
    return result


@pytest.fixture(scope="module")
def distributions(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    # `uv build` builds the source distribution, then the wheel from it:
    dist_folder = tmp_path_factory.mktemp("dist")
    run(["uv", "build", "--out-dir", str(dist_folder)], cwd=project_root)
    return dist_folder


def test_wheel_bundles_typst_packages(distributions: pathlib.Path) -> None:
    wheel = next(distributions.glob("rendercv-*.whl"))

    with zipfile.ZipFile(wheel) as wheel_zip:
        names = set(wheel_zip.namelist())

    packages = "rendercv/typst_packages/preview"
    rendercv_package = f"{packages}/rendercv/{get_rendercv_typst_version()}"
    assert f"{rendercv_package}/lib.typ" in names
    assert f"{rendercv_package}/typst.toml" in names
    assert f"{rendercv_package}/designs/classic.typ" in names
    assert f"{packages}/fontawesome/0.6.2/typst.toml" in names
    assert not any(name.startswith(f"{rendercv_package}/examples") for name in names)


def test_source_distribution_holds_only_what_builds_the_wheel(
    distributions: pathlib.Path,
) -> None:
    sdist = next(distributions.glob("rendercv-*.tar.gz"))

    with tarfile.open(sdist) as sdist_tar:
        # Without the top-level `rendercv-<version>/` folder:
        names = {name.split("/", 1)[1] for name in sdist_tar.getnames() if "/" in name}

    assert "typst/lib.typ" in names
    assert "typst/typst.toml" in names
    assert "hatch_build.py" in names
    assert "src/rendercv/__init__.py" in names
    assert "pyproject.toml" in names
    for folder in ["tests/", "docs/", "examples/", "typst/examples/", "scripts/"]:
        assert not any(name.startswith(folder) for name in names), folder


def test_rendercv_renders_offline(
    distributions: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    wheel = next(distributions.glob("rendercv-*.whl"))
    venv = tmp_path / "venv"
    if sys.platform == "win32":
        venv_python = venv / "Scripts" / "python.exe"
    else:
        venv_python = venv / "bin" / "python"
    run(["uv", "venv", str(venv), "--python", sys.executable])
    run(["uv", "pip", "install", "--python", str(venv_python), f"{wheel}[full]"])

    (tmp_path / "cv.yaml").write_text(
        "cv:\n  name: Test\n  email: test@example.com\n  sections:\n"
        "    S:\n      - bullet: hi\n",
        encoding="utf-8",
    )
    (tmp_path / "design.typ").write_text(
        f'#import "@preview/rendercv:{get_rendercv_typst_version()}": designs\n'
        "#let design = designs.moderncv()\n",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    home.mkdir()
    offline_environment = {
        **os.environ,
        # Any network access fails:
        "http_proxy": "http://0.0.0.0:1",
        "https_proxy": "http://0.0.0.0:1",
        "HTTP_PROXY": "http://0.0.0.0:1",
        "HTTPS_PROXY": "http://0.0.0.0:1",
        "no_proxy": "",
        # An empty home, so Typst can't use packages it downloaded before:
        "HOME": str(home),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        # Rich prints characters like ✓ that Windows' default encoding lacks:
        "PYTHONIOENCODING": "utf-8",
    }

    run(
        [str(venv_python), "-m", "rendercv", "render", "cv.yaml", "-nomd", "-nopng"],
        env=offline_environment,
        cwd=tmp_path,
    )

    pdf = tmp_path / "rendercv_output" / "Test_CV.pdf"
    assert pdf.read_bytes().startswith(b"%PDF")
