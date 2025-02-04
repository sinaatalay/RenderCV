import os
import pathlib
import subprocess
import sys


def create_executable():
    # Make sure the current working directory is the root of the project:
    root = pathlib.Path(__file__).parent.parent
    os.chdir(root)

    rendercv_file_path = root / "rendercv.py"
    rendercv_file_path.touch()
    rendercv_file_path.write_text("import rendercv.cli as cli; cli.app()")

    # Run pyinstaller:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--clean",
            "--collect-all",
            "rendercv",
            "--collect-all",
            "rendercv_fonts",
            "--distpath",
            "bin",
            str(rendercv_file_path),
        ],
        check=True,
    )

    # Remove the temporary file:
    rendercv_file_path.unlink()
    (root / "rendercv.spec").unlink()

    # Rename the executable:
    platform = {
        "linux": "linux",
        "darwin": "macos",
        "win32": "windows",
    }
    if sys.platform == "win32":
        executable_path = root / "bin" / "rendercv.exe"
        executable_path.rename(
            root
            / "bin"
            / f"rendercv-{platform[sys.platform]}-{os.environ['PROCESSOR_ARCHITECTURE']}"
        )
    else:
        executable_path = root / "bin" / "rendercv"
        executable_path.rename(
            root / "bin" / f"rendercv-{platform[sys.platform]}-{os.uname().machine}"
        )

    print('Executable created at "bin" folder.')  # NOQA: T201


if __name__ == "__main__":
    create_executable()
