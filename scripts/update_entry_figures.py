"""Regenerate the entry figures of the docs: each standard entry type in each design.

The figures show the sample entries in `docs/user_guide/sample_entries.yaml`, and
they are saved as `docs/assets/images/<design>/<figure name>.png`, with the figure
names the docs use. Each figure's page is only as tall as its entry.
"""

import datetime
import importlib.util
import pathlib
import shutil
import tempfile

import ruamel.yaml

from rendercv.renderer.outputs import generate_png
from rendercv.renderer.project import (
    default_design_file_name,
    load_project,
)
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.sample_generator import get_built_in_design_names
from rendercv.schema.yaml_reader import read_yaml

repository_root = pathlib.Path(__file__).parent.parent
sample_entries_path = repository_root / "docs" / "user_guide" / "sample_entries.yaml"
docs_templating_path = repository_root / "docs" / "docs_templating.py"
image_assets_directory = repository_root / "docs" / "assets" / "images"


def read_figure_names() -> dict[str, str]:
    """Read the figure file name of each entry type from the docs' templating.

    Returns:
        Entry type names mapped to figure file names without `.png`.
    """
    specification = importlib.util.spec_from_file_location(
        "docs_templating", docs_templating_path
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.figure_names


def create_figure_design(design: str) -> str:
    """Write a `design.typ` that draws a built-in design as a figure.

    Args:
        design: The built-in design's name.

    Returns:
        The Typst source: the design without its footer and top note, on a page
        as tall as its content.
    """
    return f"""#import "@preview/rendercv:{get_rendercv_typst_version()}": designs

#let figure-design = designs.{design}(
  page: (show_footer: false, show_top_note: false, top_margin: 30pt, bottom_margin: 30pt),
)
#let design = figure-design + (
  document: (body, info) => (figure-design.document)({{
    set page(height: auto)
    body
  }}, info),
)
"""


figure_names = read_figure_names()
sample_entries = read_yaml(sample_entries_path)
yaml = ruamel.yaml.YAML()

with tempfile.TemporaryDirectory() as temporary_directory:
    temporary_path = pathlib.Path(temporary_directory)
    yaml_file_path = temporary_path / "cv.yaml"
    for design in get_built_in_design_names():
        (temporary_path / default_design_file_name).write_text(
            create_figure_design(design), encoding="utf-8"
        )
        output_directory = image_assets_directory / design
        output_directory.mkdir(parents=True, exist_ok=True)
        for entry_type, entry in sample_entries.items():
            with yaml_file_path.open("w", encoding="utf-8") as yaml_file:
                yaml.dump(
                    {
                        "cv": {"sections": {entry_type: [entry]}},
                        "settings": {"current_date": datetime.date(2025, 1, 1)},
                    },
                    yaml_file,
                )
            project = load_project(
                yaml_file_path,
                png_path=temporary_path / "figure.png",
                dont_generate_typst=True,
                dont_generate_pdf=True,
                dont_generate_markdown=True,
                dont_generate_html=True,
            )
            first_page, *_ = generate_png(project) or []
            shutil.copy(
                first_page, output_directory / f"{figure_names[entry_type]}.png"
            )

print("Entry figures generated successfully.")  # NOQA: T201
