import pathlib
from collections.abc import Callable

from rendercv.schema.yaml_reader import read_yaml

type RunScript = Callable[..., None]


def test_update_entry_figures(
    run_script: RunScript, tmp_path: pathlib.Path, two_designs: tuple[str, ...]
) -> None:
    run_script(
        "update_entry_figures.py",
        "docs/user_guide/sample_entries.yaml",
        "docs/docs_templating.py",
    )

    sample_entries = read_yaml(tmp_path / "docs" / "user_guide" / "sample_entries.yaml")
    images = tmp_path / "docs" / "assets" / "images"
    assert {path.name for path in images.iterdir()} == set(two_designs)
    for design in two_designs:
        figures = list((images / design).iterdir())
        assert len(figures) == len(sample_entries)
        for figure in figures:
            png = figure.read_bytes()
            assert png.startswith(b"\x89PNG")
            # Cropped to the entry: much wider than tall, unlike a page:
            width, height = int.from_bytes(png[16:20]), int.from_bytes(png[20:24])
            assert width > 2 * height
