import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def generate_text(rendercv_model: RenderCVModel) -> pathlib.Path | None:
    """Generate plain text file from CV model via Jinja2 templates.

    Why:
        Plain text provides a universally readable CV format for terminals,
        emails, and text-only pipelines where no markup renderer is available.

    Args:
        rendercv_model: Validated CV model with content.

    Returns:
        Path to generated plain text file, or None if generation disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_text:
        return None
    text_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.text_path
    )
    text_contents = render_full_template(rendercv_model, "text")
    text_path.write_text(text_contents, encoding="utf-8")
    return text_path
