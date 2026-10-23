import pytest

from rendercv_fonts import available_font_families, path_of, paths_to_font_folders


def test_available_font_families():
    assert len(available_font_families) == len(paths_to_font_folders)


@pytest.mark.parametrize("font_family", available_font_families)
def test_font_folders_exist(font_family):
    folder = path_of[font_family]
    assert (
        sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        > 0.05 * 1024 * 1024
    )
