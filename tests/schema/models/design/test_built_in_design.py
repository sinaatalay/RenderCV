from pathlib import Path
from typing import get_args

import pytest

from rendercv.schema.models.design.built_in_design import (
    BuiltInDesign,
    available_themes,
)
from rendercv.schema.models.design.classic_theme import ClassicTheme

theme_classes: list[type[ClassicTheme]] = list(
    get_args(get_args(BuiltInDesign.__value__)[0])
)


def test_available_themes():
    """Test that available_themes includes all theme YAML files + ClassicTheme."""
    other_themes_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "src"
        / "rendercv"
        / "schema"
        / "models"
        / "design"
        / "other_themes"
    )

    yaml_files_count = len(list(other_themes_dir.glob("*.yaml")))
    expected_theme_count = yaml_files_count + 1  # +1 for ClassicTheme

    assert len(available_themes) == expected_theme_count


@pytest.mark.parametrize(
    "theme_class",
    theme_classes,
    ids=[theme_class.model_fields["theme"].default for theme_class in theme_classes],
)
def test_education_entry_does_not_render_degree_twice(
    theme_class: type[ClassicTheme],
) -> None:
    """A theme whose main column already shows the degree must not also have a
    degree column, or the degree is printed twice."""
    education_entry = theme_class().templates.education_entry

    if "DEGREE" in education_entry.main_column:
        assert education_entry.degree_column is None
