"""Test that RenderCV installs and renders CVs in Pyodide (Python in the browser).

Why:
    The web app at rendercv.com runs RenderCV in Pyodide. Every dependency needs
    a Pyodide build (Typst has a `pyemscripten` wheel on PyPI), and the Typst
    packages must come from the wheel, since there is no file system cache.
"""

import pathlib
import shutil
import subprocess

import pytest

project_root = pathlib.Path(__file__).parent.parent
# Pyodide 314 has the ABI (`pyemscripten_2026_0`) Typst's Pyodide wheel is built for:
pyodide_package = "pyodide@314"


@pytest.fixture
def js_runtime(tmp_path: pathlib.Path) -> str:
    """Provide a JavaScript runtime with Pyodide installed in `tmp_path`.

    Why:
        Bun is preferred; Node.js with npm is used if Bun isn't installed, and
        Bun is installed into `tmp_path` if neither is. Pyodide is installed
        into `tmp_path` so `node_modules` never touches the repository.

    Returns:
        The path of the runtime's executable.
    """
    bun = shutil.which("bun")
    node = shutil.which("node")
    npm = shutil.which("npm")
    if bun is None and node is not None and npm is not None:
        for arguments in (["init", "-y"], ["install", pyodide_package]):
            subprocess.run(
                [npm, *arguments],
                cwd=tmp_path,
                check=True,
                capture_output=True,
                timeout=300,
            )
        return node

    if bun is None:
        bun_folder = tmp_path / "bun"
        subprocess.run(
            [
                "bash",
                "-c",
                f"curl -fsSL https://bun.sh/install | BUN_INSTALL={bun_folder} bash",
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
        bun = str(bun_folder / "bin" / "bun")

    subprocess.run(
        [bun, "add", pyodide_package],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        timeout=300,
    )
    return bun


def test_rendercv_renders_in_pyodide(tmp_path: pathlib.Path, js_runtime: str) -> None:
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path / "dist")],
        cwd=project_root,
        check=True,
        capture_output=True,
        timeout=300,
    )
    wheel = next((tmp_path / "dist").glob("rendercv-*-py3-none-any.whl"))

    script = tmp_path / "test.mjs"
    # Forward slashes, so the path works on Windows too:
    script.write_text(
        f"""\
import fs from "node:fs";
import {{ loadPyodide }} from "pyodide";

const pyodide = await loadPyodide();
// Copy the wheel into Pyodide's file system, to avoid file:// URLs on Windows:
pyodide.FS.writeFile("/tmp/{wheel.name}", fs.readFileSync("{wheel.resolve().as_posix()}"));
await pyodide.loadPackage("micropip");
await pyodide.runPythonAsync(`
import micropip

# micropip may not resolve the extra of pydantic[email]:
await micropip.install("email-validator")
await micropip.install("emfs:/tmp/{wheel.name}")

import pathlib

from rendercv.renderer.outputs import generate_markdown, generate_pdf
from rendercv.renderer.project import load_project

yaml_file = pathlib.Path("/home/pyodide/cv.yaml")
yaml_file.write_text("cv:\\\\n  name: John Doe\\\\n  sections:\\\\n    Skills:\\\\n      - bullet: Typst\\\\n")
project = load_project(yaml_file)
print("PDF:", generate_pdf(project).read_bytes()[:5])
print(generate_markdown(project).read_text())
`);
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [js_runtime, str(script)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
        cwd=tmp_path,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, f"Pyodide failed:\n{output}"
    assert "PDF: b'%PDF-'" in result.stdout
    assert "# John Doe" in result.stdout
    assert "- Typst" in result.stdout
