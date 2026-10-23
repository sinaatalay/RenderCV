import importlib.metadata
import pathlib
from urllib.parse import unquote, urlsplit

import pytest
import rendercv_fonts
from fontTools.ttLib import TTFont
from rendercv_fonts import (
    available_font_families,
    links_to_font_files,
    path_of,
    paths_to_font_files,
    paths_to_font_folders,
)


def test_available_font_families() -> None:
    assert len(available_font_families) == len(paths_to_font_folders)


@pytest.mark.parametrize("font_family", available_font_families)
def test_font_folders_exist(font_family: str) -> None:
    folder = path_of[font_family]
    assert (
        sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        > 0.05 * 1024 * 1024
    )


def test_version_matches_distribution() -> None:
    assert rendercv_fonts.__version__ == importlib.metadata.version("rendercv-fonts")


def test_font_files_match_inventory() -> None:
    package_path = pathlib.Path(rendercv_fonts.__file__).parent
    expected = {
        path
        for path in package_path.rglob("*")
        if path.suffix.lower() in {".otf", ".ttf"}
    }
    assert set(paths_to_font_files) == expected
    assert len(paths_to_font_files) == len(expected)
    assert len(links_to_font_files) == len(paths_to_font_files)


@pytest.mark.parametrize(
    ("font_path", "url"),
    list(zip(paths_to_font_files, links_to_font_files, strict=True)),
)
def test_download_links_point_to_monorepo(font_path: pathlib.Path, url: str) -> None:
    package_path = pathlib.Path(rendercv_fonts.__file__).parent
    parsed_url = urlsplit(url)
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == "raw.githubusercontent.com"
    assert unquote(parsed_url.path) == (
        "/rendercv/rendercv/main/packages/rendercv-fonts/src/rendercv_fonts/"
        + font_path.relative_to(package_path).as_posix()
    )
    assert " " not in url
    assert "\\" not in url


@pytest.mark.parametrize("font_path", sorted(path_of["Font Awesome 7"].glob("*.otf")))
def test_fontawesome_version(font_path: pathlib.Path) -> None:
    with TTFont(font_path) as font:
        version: str | None = font["name"].getDebugName(5)
        assert version is not None
        assert version.endswith("(Font Awesome version: 7.3.1)")


def test_fontawesome_includes_codeberg() -> None:
    """Keep the Codeberg icon available to the Font Awesome 7.3 icon map.

    Why:
        Font Awesome 7.0 silently rendered a missing glyph for this brand.
    """
    with TTFont(
        path_of["Font Awesome 7"] / "Font Awesome 7 Brands-Regular-400.otf"
    ) as font:
        cmap: dict[int, str] | None = font.getBestCmap()
        assert cmap is not None
        assert 0xE8AD in cmap
