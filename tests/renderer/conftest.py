import datetime
import pathlib
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.renderer.project import Project, load_project
from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import EntryTypeDeclaration
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_commented_map,
)
from rendercv.schema.sample_generator import create_sample_yaml_input_file

# Snapshots must not change with the day the tests run:
pinned_current_date = datetime.date(2025, 6, 1)

profile_picture_path = (
    pathlib.Path(__file__).parent / "testdata" / "profile_picture.jpg"
)


@pytest.fixture(scope="session")
def standard_entry_types() -> dict[str, EntryTypeDeclaration]:
    return read_standard_entry_types()


@pytest.fixture
def build_model(
    standard_entry_types: dict[str, EntryTypeDeclaration],
) -> Callable[..., RenderCVModel]:
    """Build a validated model from a `cv` mapping, with the date pinned."""

    def build(cv: dict[str, Any], **top_level: Any) -> RenderCVModel:
        settings = {
            "current_date": pinned_current_date,
            **top_level.pop("settings", {}),
        }
        return build_rendercv_model_from_commented_map(
            {"cv": cv, "settings": settings, **top_level},
            entry_types=standard_entry_types,
        )

    return build


@pytest.fixture
def sample_yaml() -> str:
    return (
        create_sample_yaml_input_file()
        + f"settings:\n  current_date: {pinned_current_date.isoformat()}\n"
    )


@pytest.fixture
def load_cv(tmp_path: pathlib.Path) -> Callable[..., Project]:
    """Write a CV (and any Typst files next to it) to a folder and load it."""

    def load(yaml: str, files: dict[str, str] | None = None, **kwargs: Any) -> Project:
        for name, content in (files or {}).items():
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        input_file_path = tmp_path / "cv.yaml"
        input_file_path.write_text(yaml, encoding="utf-8")
        return load_project(input_file_path, **kwargs)

    return load


@pytest.fixture
def sample_project(load_cv: Callable[..., Project], sample_yaml: str) -> Project:
    return load_cv(sample_yaml)
