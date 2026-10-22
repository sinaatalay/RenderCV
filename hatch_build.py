"""Build hook that bundles Typst packages into the RenderCV wheel.

RenderCV's own Typst package lives in `typst/` at the repository root, and it
depends on packages from Typst Universe. For RenderCV to work offline, the wheel
ships all of them under `rendercv/typst_packages/preview/<name>/<version>/`,
the layout Typst reads packages from.

External packages are pinned by version and SHA-256 and downloaded when the
wheel is built. To build without internet access, set
`RENDERCV_TYPST_PACKAGES_CACHE` to a folder that already holds the archives
(`<name>-<version>.tar.gz`).
"""

import hashlib
import io
import os
import pathlib
import tarfile
import tempfile
import tomllib
import urllib.request
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Typst Universe packages RenderCV's Typst package imports:
# name -> (version, SHA-256 of the archive)
external_typst_packages: dict[str, tuple[str, str]] = {
    "fontawesome": (
        "0.6.2",
        "0ad8435267760fa7b35dc468c350eb614a88670d264e058147b113047c0fb54d",
    ),
}

# Files of the RenderCV Typst package that are needed at runtime:
rendercv_typst_package_files = ("typst.toml", "lib.typ", "LICENSE")
rendercv_typst_package_folders = ("src", "entries", "designs")


def fetch_archive(name: str, version: str, sha256: str) -> bytes:
    """Get a Typst Universe package archive, checking its SHA-256.

    Args:
        name: The package's name.
        version: The package's version.
        sha256: The archive's expected SHA-256.

    Returns:
        The archive's bytes.
    """
    file_name = f"{name}-{version}.tar.gz"
    cache = os.environ.get("RENDERCV_TYPST_PACKAGES_CACHE")
    if cache and (pathlib.Path(cache) / file_name).is_file():
        archive = (pathlib.Path(cache) / file_name).read_bytes()
    else:
        url = f"https://packages.typst.org/preview/{file_name}"
        with urllib.request.urlopen(url, timeout=60) as response:
            archive = response.read()
    if hashlib.sha256(archive).hexdigest() != sha256:
        message = f"The archive of the Typst package {name} {version} has an unexpected SHA-256."
        raise RuntimeError(message)
    return archive


class CustomBuildHook(BuildHookInterface):
    """Adds RenderCV's Typst package and its dependencies to the wheel."""

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Add the Typst packages to the wheel's files.

        Args:
            version: The kind of build: "standard" or "editable".
            build_data: Build data hatchling passes to hooks.
        """
        if self.target_name != "wheel" or version == "editable":
            # Source distributions ship `typst/` as source, and editable
            # installs read it (and download dependencies) directly.
            return

        root = pathlib.Path(self.root)
        force_include: dict[str, str] = build_data.setdefault("force_include", {})

        typst_package = root / "typst"
        typst_version = tomllib.loads((typst_package / "typst.toml").read_text())[
            "package"
        ]["version"]
        destination = f"rendercv/typst_packages/preview/rendercv/{typst_version}"
        for file_name in rendercv_typst_package_files:
            force_include[str(typst_package / file_name)] = f"{destination}/{file_name}"
        for folder in rendercv_typst_package_folders:
            force_include[str(typst_package / folder)] = f"{destination}/{folder}"

        staging = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-typst-packages-"))
        for name, (package_version, sha256) in external_typst_packages.items():
            archive = fetch_archive(name, package_version, sha256)
            package_folder = staging / name / package_version
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
                tar.extractall(package_folder, filter="data")
            force_include[str(package_folder)] = (
                f"rendercv/typst_packages/preview/{name}/{package_version}"
            )
