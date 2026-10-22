"""Regenerate `examples/`: one folder per built-in design, as `rendercv new` makes.

Each folder holds the sample YAML, a `design.typ` choosing the design, and the
rendered PDF. The first page of each is also saved as the design's image in the
docs.
"""

import pathlib
import shutil
import tempfile

from rendercv.renderer.outputs import generate_pdf, generate_png
from rendercv.renderer.project import default_design_file_name, load_project
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_yaml_input_file,
    get_built_in_design_names,
)

repository_root = pathlib.Path(__file__).parent.parent
examples_directory = repository_root / "examples"
image_assets_directory = repository_root / "docs" / "assets" / "images" / "examples"
yaml_file_name = "John_Doe_CV.yaml"

shutil.rmtree(examples_directory, ignore_errors=True)
image_assets_directory.mkdir(parents=True, exist_ok=True)

for design in get_built_in_design_names():
    design_directory = examples_directory / design
    design_directory.mkdir(parents=True)
    yaml_file_path = design_directory / yaml_file_name
    yaml_file_path.write_text(
        create_sample_yaml_input_file(name="John Doe", locale="english"),
        encoding="utf-8",
    )
    (design_directory / default_design_file_name).write_text(
        create_sample_design_file(design), encoding="utf-8"
    )

    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_path = pathlib.Path(temporary_directory)
        project = load_project(
            yaml_file_path,
            pdf_path=design_directory / f"{yaml_file_path.stem}.pdf",
            png_path=temporary_path / f"{yaml_file_path.stem}.png",
            dont_generate_typst=True,
            dont_generate_markdown=True,
            dont_generate_html=True,
        )
        generate_pdf(project)
        first_page, *_ = generate_png(project) or []
        shutil.copy(first_page, image_assets_directory / f"{design}.png")

print("Examples generated successfully.")  # NOQA: T201
