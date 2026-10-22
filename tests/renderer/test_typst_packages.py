import pathlib
import tomllib

import pytest

from rendercv.exception import RenderCVInternalError, RenderCVUserError
from rendercv.renderer import typst_packages
from rendercv.renderer.typst_packages import (
    add_version_aliases,
    find_rendercv_typst_package,
    get_package_path,
    get_rendercv_typst_version,
    rendercv_import_pattern,
    source_typst_package_directory,
)


def write_package(directory: pathlib.Path, version: str) -> pathlib.Path:
    package = directory / "preview" / "rendercv" / version
    package.mkdir(parents=True)
    (package / "typst.toml").write_text(
        f'[package]\nname = "rendercv"\nversion = "{version}"\n', encoding="utf-8"
    )
    (package / "lib.typ").write_text("", encoding="utf-8")
    return package


class TestFindRendercvTypstPackage:
    def test_finds_the_source_checkout(self) -> None:
        # The tests run from a source checkout, without a bundled package:
        assert find_rendercv_typst_package() == source_typst_package_directory
        assert (source_typst_package_directory / "lib.typ").is_file()

    def test_prefers_the_bundled_package(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        bundled = write_package(tmp_path, "3.1.0")
        monkeypatch.setattr(typst_packages, "bundled_packages_directory", tmp_path)

        assert find_rendercv_typst_package() == bundled

    def test_raises_if_the_package_is_missing(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(typst_packages, "bundled_packages_directory", tmp_path)
        monkeypatch.setattr(
            typst_packages, "source_typst_package_directory", tmp_path / "missing"
        )

        with pytest.raises(RenderCVInternalError, match="Typst package is missing"):
            find_rendercv_typst_package()


def test_get_rendercv_typst_version() -> None:
    manifest = tomllib.loads(
        (source_typst_package_directory / "typst.toml").read_text(encoding="utf-8")
    )

    assert get_rendercv_typst_version() == manifest["package"]["version"]
    assert rendercv_import_pattern.fullmatch(
        f"@preview/rendercv:{get_rendercv_typst_version()}"
    )


class TestGetPackagePath:
    def test_serves_the_source_package(self) -> None:
        package = get_package_path() / "preview" / "rendercv"
        version = get_rendercv_typst_version()

        assert get_package_path() is get_package_path()
        assert (package / version / "typst.toml").is_file()
        assert (package / version / "lib.typ").is_file()
        assert (package / version / "src" / "render.typ").is_file()
        assert (package / version / "entries" / "standard.typ").is_file()
        assert (package / version / "designs" / "engine.typ").is_file()
        assert not (package / version / "examples").exists()

    def test_copies_the_bundled_packages(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        bundled = tmp_path / "bundled"
        write_package(bundled, "3.0.0")
        fontawesome = bundled / "preview" / "fontawesome" / "0.6.2"
        fontawesome.mkdir(parents=True)
        (fontawesome / "typst.toml").write_text("", encoding="utf-8")
        monkeypatch.setattr(typst_packages, "bundled_packages_directory", bundled)

        package_path = get_package_path.__wrapped__()

        assert (package_path / "preview" / "rendercv" / "3.0.0" / "lib.typ").is_file()
        assert (package_path / "preview" / "fontawesome" / "0.6.2").is_dir()


class TestAddVersionAliases:
    @pytest.fixture
    def package_path(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> pathlib.Path:
        package_path = tmp_path / "packages"
        write_package(package_path, "3.2.0")
        monkeypatch.setattr(typst_packages, "get_package_path", lambda: package_path)
        monkeypatch.setattr(
            typst_packages, "get_rendercv_typst_version", lambda: "3.2.0"
        )
        return package_path

    def write_typst_file(self, tmp_path: pathlib.Path, version: str) -> pathlib.Path:
        typst_file = tmp_path / "design.typ"
        typst_file.write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            "#let design = designs.classic()\n",
            encoding="utf-8",
        )
        return typst_file

    @pytest.mark.parametrize("version", ["3.0.0", "3.1.9", "3.2.0"])
    def test_serves_older_versions_of_the_same_major_version(
        self, tmp_path: pathlib.Path, package_path: pathlib.Path, version: str
    ) -> None:
        add_version_aliases([self.write_typst_file(tmp_path, version)])

        alias = package_path / "preview" / "rendercv" / version
        assert (alias / "typst.toml").is_file()
        assert (alias / "lib.typ").is_file()

    def test_aliases_every_import_of_every_file(
        self, tmp_path: pathlib.Path, package_path: pathlib.Path
    ) -> None:
        entries_file = tmp_path / "entries.typ"
        entries_file.write_text(
            '#import "@preview/rendercv:3.0.0": *\n'
            '#import "@preview/rendercv:3.1.0": entry-type\n',
            encoding="utf-8",
        )
        design_file = self.write_typst_file(tmp_path, "3.0.1")

        add_version_aliases([entries_file, design_file])

        versions = {
            path.name for path in (package_path / "preview" / "rendercv").iterdir()
        }
        assert versions == {"3.0.0", "3.0.1", "3.1.0", "3.2.0"}

    def test_ignores_files_without_rendercv_imports(
        self, tmp_path: pathlib.Path, package_path: pathlib.Path
    ) -> None:
        typst_file = tmp_path / "entries.typ"
        typst_file.write_text('#import "@preview/other:1.0.0": *\n', encoding="utf-8")

        add_version_aliases([typst_file])

        assert [
            path.name for path in (package_path / "preview" / "rendercv").iterdir()
        ] == ["3.2.0"]

    @pytest.mark.parametrize("version", ["3.3.0", "3.2.1", "4.0.0", "2.9.9"])
    def test_rejects_newer_and_other_major_versions(
        self, tmp_path: pathlib.Path, package_path: pathlib.Path, version: str
    ) -> None:
        typst_file = self.write_typst_file(tmp_path, version)

        with pytest.raises(RenderCVUserError) as error:
            add_version_aliases([typst_file])

        assert error.value.message == (
            f"`design.typ` imports `@preview/rendercv:{version}`, but this RenderCV"
            " comes with version 3.2.0. Change the import to"
            " `@preview/rendercv:3.2.0`."
        )
        assert not (package_path / "preview" / "rendercv" / version).exists()

    def test_works_with_the_real_package(self, tmp_path: pathlib.Path) -> None:
        version = get_rendercv_typst_version()

        add_version_aliases([self.write_typst_file(tmp_path, version)])

        assert (get_package_path() / "preview" / "rendercv" / version).is_dir()
