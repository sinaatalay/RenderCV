import os
import pathlib
import platform
import subprocess
import sys
import tempfile
import zipfile

root_path = pathlib.Path(__file__).parent.parent

platform_names = {
    "linux": "linux",
    "darwin": "macos",
    "win32": "windows",
}

machine_names = {
    "AMD64": "x86_64",
    "x86_64": "x86_64",
    "aarch64": "ARM64",
    "arm64": "ARM64",
}

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = pathlib.Path(temp_dir)

    # Build the wheel and unpack it, so the executable gets the Typst packages
    # the build hook bundles:
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(temp_path / "dist")],
        cwd=root_path,
        check=True,
    )
    wheel = next((temp_path / "dist").glob("rendercv-*.whl"))
    with zipfile.ZipFile(wheel) as wheel_zip:
        wheel_zip.extractall(temp_path)

    # Create entry point script
    rendercv_file = temp_path / "rendercv.py"
    rendercv_file.write_text("import rendercv.cli.app as app; app.app()")

    # Run PyInstaller. `PYTHONPATH` makes it bundle RenderCV from the unpacked
    # wheel instead of the (editable) RenderCV of this environment:
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
            # Rich imports its Unicode tables by name, which PyInstaller can't see:
            "--collect-submodules",
            "rich._unicode_data",
            "--distpath",
            "bin",
            str(rendercv_file),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": str(temp_path)},
    )

    # Determine executable name based on platform
    platform_name = platform_names[sys.platform]
    machine_name = machine_names[platform.machine()]

    # Get original and new executable paths
    match sys.platform:
        case "win32":
            original_name = "rendercv.exe"
            new_name = f"rendercv-{platform_name}-{machine_name}.exe"
        case _:
            original_name = "rendercv"
            new_name = f"rendercv-{platform_name}-{machine_name}"

    original_path = root_path / "bin" / original_name
    executable_path = root_path / "bin" / new_name
    original_path.rename(executable_path)

# Create zip archive with preserved executable permissions
zip_path = executable_path.with_suffix(".zip")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipinfo = zipfile.ZipInfo(executable_path.name)
    # Set Unix executable permissions (rwxr-xr-x) - 0o755 shifted to external_attr position
    zipinfo.external_attr = 0o755 << 16
    zipf.writestr(zipinfo, executable_path.read_bytes())
