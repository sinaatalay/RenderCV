import pathlib
import shutil
from collections.abc import Callable, Mapping

import pydantic
import pytest

from rendercv.renderer.outputs import generate_pdf
from rendercv.renderer.project import Project, load_project
from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import (
    EntryTypeDeclaration,
    build_entry_type_models,
)

type RenderPdf = Callable[[pathlib.Path], tuple[Project, pathlib.Path]]


@pytest.fixture
def render_pdf() -> RenderPdf:
    # Renders a CV's YAML file (with the `design.typ` and `entries.typ` next to
    # it) through RenderCV, to check that generated files really work:
    def render(yaml_file: pathlib.Path) -> tuple[Project, pathlib.Path]:
        project = load_project(yaml_file)
        pdf = generate_pdf(project)
        assert pdf is not None
        assert pdf.read_bytes().startswith(b"%PDF")
        return project, pdf

    return render


@pytest.fixture(scope="session")
def standard_entry_types() -> Mapping[str, EntryTypeDeclaration]:
    # Read from the real Typst package once per test session (it compiles Typst):
    return read_standard_entry_types()


@pytest.fixture(scope="session")
def standard_entry_type_models(
    standard_entry_types: Mapping[str, EntryTypeDeclaration],
) -> Mapping[str, type[pydantic.BaseModel]]:
    return build_entry_type_models(standard_entry_types)


@pytest.fixture
def input_file_path(tmp_path: pathlib.Path) -> pathlib.Path:
    input_file_path = pathlib.Path(__file__).parent / "testdata" / "input_file.yaml"
    shutil.copyfile(input_file_path, tmp_path / input_file_path.name)
    return tmp_path / input_file_path.name
