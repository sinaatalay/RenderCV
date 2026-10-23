from pathlib import Path

import pytest

from rendercv.schema.models.design.built_in_design import (
    available_themes,
    built_in_theme_models,
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


@pytest.mark.parametrize("theme", available_themes)
def test_partial_font_override_preserves_theme_defaults(theme: str) -> None:
    model = built_in_theme_models[theme]
    default = model()
    customized = model.model_validate(
        {"typography": {"font_family": {"body": "Arial"}}}
    )
    assert customized.typography.font_family.body == "Arial"
    assert customized.typography.font_family.name == default.typography.font_family.name
    assert type(customized.typography.font_family) is type(
        default.typography.font_family
    )
    customized.model_dump_json(warnings="error")
