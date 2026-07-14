import pytest

from rendercv.renderer.text import generate_text
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_text(
    compare_file_with_reference,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.text_path = output_path
        generate_text(model)

    reference_filename = f"{cv_variant}.txt"
    assert compare_file_with_reference(generate_file, reference_filename)
