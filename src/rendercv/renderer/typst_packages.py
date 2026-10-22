import atexit
import functools
import pathlib
import re
import shutil
import tempfile
import tomllib

from rendercv.exception import RenderCVInternalError, RenderCVUserError

# Where the build hook puts the Typst packages RenderCV ships with.
bundled_packages_directory = pathlib.Path(__file__).parent.parent / "typst_packages"
# Where the RenderCV Typst package lives in a source checkout.
source_typst_package_directory = pathlib.Path(__file__).parents[3] / "typst"

rendercv_import_pattern = re.compile(r"@preview/rendercv:(\d+)\.(\d+)\.(\d+)")


def find_rendercv_typst_package() -> pathlib.Path:
    """Find the RenderCV Typst package: bundled in the wheel, or in the checkout.

    Why:
        Installed RenderCV ships its Typst package inside the Python package.
        In a source checkout, the package lives in the repository's `typst/`
        folder instead, so development needs no build step.

    Returns:
        The folder containing the package's `typst.toml`.
    """
    for directory in sorted(bundled_packages_directory.glob("preview/rendercv/*")):
        if (directory / "typst.toml").is_file():
            return directory
    if (source_typst_package_directory / "typst.toml").is_file():
        return source_typst_package_directory
    message = "RenderCV's Typst package is missing. Reinstall RenderCV."
    raise RenderCVInternalError(message)


@functools.cache
def get_rendercv_typst_version() -> str:
    """Return the version of the RenderCV Typst package, like "3.0.0"."""
    manifest = find_rendercv_typst_package() / "typst.toml"
    return tomllib.loads(manifest.read_text(encoding="utf-8"))["package"]["version"]


@functools.cache
def get_package_path() -> pathlib.Path:
    """Set up the folder Typst finds RenderCV's packages in.

    Why:
        Typst looks for `@preview/name:version` packages in a folder laid out
        as `preview/name/version/`. RenderCV's own Typst package and the
        packages it depends on (bundled at build time, so no internet is
        needed) are copied there once per run.

    Returns:
        The package folder.
    """
    package_path = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-typst-packages-"))
    atexit.register(shutil.rmtree, str(package_path), True)

    if bundled_packages_directory.is_dir():
        shutil.copytree(bundled_packages_directory, package_path, dirs_exist_ok=True)
    else:
        shutil.copytree(
            source_typst_package_directory,
            package_path / "preview" / "rendercv" / get_rendercv_typst_version(),
            ignore=shutil.ignore_patterns("examples", "tests", "*.pdf", "*.png"),
        )
    return package_path


def add_version_aliases(typst_files: list[pathlib.Path]) -> None:
    """Let user Typst files import older versions of the RenderCV package.

    Why:
        A `design.typ` written for RenderCV 3.0 imports
        `@preview/rendercv:3.0.0`. After upgrading to 3.2, that import should
        still work, so every older 3.x version a user file asks for is served
        by the bundled package.

    Args:
        typst_files: The user's Typst files.

    Raises:
        RenderCVUserError: If a file asks for a newer version or another major
            version than the bundled one.
    """
    version = get_rendercv_typst_version()
    bundled = tuple(int(part) for part in version.split("."))
    package_directory = get_package_path() / "preview" / "rendercv"
    for typst_file in typst_files:
        for match in rendercv_import_pattern.finditer(
            typst_file.read_text(encoding="utf-8")
        ):
            requested = tuple(int(part) for part in match.groups())
            requested_text = ".".join(match.groups())
            if requested[0] != bundled[0] or requested > bundled:
                message = (
                    f"`{typst_file.name}` imports `@preview/rendercv:{requested_text}`,"
                    f" but this RenderCV comes with version {version}. Change the"
                    f" import to `@preview/rendercv:{version}`."
                )
                raise RenderCVUserError(message)
            alias = package_directory / requested_text
            if not alias.exists():
                shutil.copytree(package_directory / version, alias)
