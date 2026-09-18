import pytest

from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_dictionary_and_model,
)


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_typst(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path
        generate_typst(model)

    reference_filename = f"{theme}_{cv_variant}.typ"
    assert compare_file_with_reference(generate_file, reference_filename)


def test_generate_typst_preserves_nested_highlight_indentation(tmp_path):
    yaml = """cv:
  name: John Doe
  sections:
    experience:
      - company: Example Company
        position: Engineer
        highlights:
          - Main bullet point
            - Sub-bullet 1
            - Sub-bullet 2
"""
    _, model = build_rendercv_dictionary_and_model(
        yaml,
        typst_path=tmp_path / "nested-highlights.typ",
    )

    typst_path = generate_typst(model)

    assert typst_path is not None
    highlight_lines = [
        line
        for line in typst_path.read_text(encoding="utf-8").splitlines()
        if "bullet point" in line or "Sub-bullet" in line
    ]
    assert highlight_lines == [
        "    - Main bullet point",
        "      - Sub-bullet 1",
        "      - Sub-bullet 2",
    ]
