import pathlib
from collections.abc import Callable

from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_yaml_input_file,
)

type RunScript = Callable[..., None]


def test_update_examples(
    run_script: RunScript, tmp_path: pathlib.Path, two_designs: tuple[str, ...]
) -> None:
    (tmp_path / "examples" / "removed_design").mkdir(parents=True)

    run_script("update_examples.py")

    examples = tmp_path / "examples"
    assert {path.name for path in examples.iterdir()} == set(two_designs)
    for design in two_designs:
        assert (examples / design / "John_Doe_CV.yaml").read_text(
            encoding="utf-8"
        ) == create_sample_yaml_input_file(name="John Doe", locale="english")
        assert (examples / design / "design.typ").read_text(
            encoding="utf-8"
        ) == create_sample_design_file(design)
        assert (examples / design / "John_Doe_CV.pdf").read_bytes().startswith(b"%PDF")
        image = tmp_path / "docs" / "assets" / "images" / "examples" / f"{design}.png"
        assert image.read_bytes().startswith(b"\x89PNG")
