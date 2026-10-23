import pathlib
import shutil

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def render_typst_source(rendercv_model: RenderCVModel) -> str:
    """Render the Typst source of a CV.

    Why:
        The source is rendered once, then saved and compiled to PDF, PNG, and SVG
        as requested. Compiling doesn't need a saved Typst file.

    Args:
        rendercv_model: Validated CV model.

    Returns:
        The Typst source.
    """
    return render_full_template(rendercv_model, "typst")


def generate_typst(
    rendercv_model: RenderCVModel, source: str | None = None
) -> pathlib.Path | None:
    """Save the Typst source of a CV, unless disabled.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, if already rendered.

    Returns:
        Path to the Typst file, or None if its generation is disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_typst:
        return None
    typst_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.typst_path
    )
    if source is None:
        source = render_typst_source(rendercv_model)
    typst_path.write_text(source, encoding="utf-8")
    copy_photo_next_to_typst_file(rendercv_model, typst_path.parent)
    return typst_path


def copy_photo_next_to_typst_file(
    rendercv_model: RenderCVModel, directory: pathlib.Path
) -> None:
    """Copy the CV's photo into the directory of its Typst file.

    Why:
        The Typst source refers to the photo by its file name, so that a saved
        Typst file compiles on its own, wherever the photo came from.

    Args:
        rendercv_model: CV model whose photo, if any, is a local file.
        directory: Directory of the Typst file.
    """
    photo = rendercv_model.cv.photo
    if not isinstance(photo, pathlib.Path):
        return
    copy = directory / photo.name
    if not (copy.exists() and copy.samefile(photo)):
        shutil.copy(photo, copy)
