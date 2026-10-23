import pathlib
import re

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.model_processor import build_document_placeholders
from .templater.segments import substitute_placeholders


def resolve_output_folder_placeholder(
    file_path: pathlib.Path, output_folder: pathlib.Path
) -> pathlib.Path:
    """Replace the OUTPUT_FOLDER directory component with the actual output folder.

    Why:
        Output file paths use OUTPUT_FOLDER as a placeholder directory so users
        can redirect all output via the single ``output_folder`` setting. Both
        paths are already absolute (resolved by PlannedPathRelativeToInput from
        the same base), so the replacement swaps the placeholder component and
        appends remaining path segments.

    Args:
        file_path: Absolute path potentially containing an OUTPUT_FOLDER component.
        output_folder: Absolute path to the actual output folder.

    Returns:
        Path with OUTPUT_FOLDER replaced, or original path if not present.
    """
    parts = file_path.parts
    if "OUTPUT_FOLDER" not in parts:
        return file_path

    idx = parts.index("OUTPUT_FOLDER")
    suffix_parts = parts[idx + 1 :]

    if suffix_parts:
        return output_folder / pathlib.Path(*suffix_parts)
    return output_folder


# Characters that can't be in a file name on some operating system, like `/`:
invalid_file_name_characters = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def resolve_rendercv_file_path(
    rendercv_model: RenderCVModel, file_path: pathlib.Path
) -> pathlib.Path:
    """Resolve output file path with placeholder substitution and directory creation.

    Why:
        Users specify output paths like ``OUTPUT_FOLDER/NAME_CV_YEAR.pdf`` with
        placeholders for dynamic naming. This function first resolves the
        OUTPUT_FOLDER directory component to the configured output folder, then
        substitutes name and date placeholders in the filename, and finally
        creates parent directories as needed. Characters of values that can't
        be in a file name (`/`, `:`, ...) are replaced by `_`.

    Example:
        ```py
        # Given model with name="John Doe", year=2025, output_folder=rendercv_output
        path = resolve_rendercv_file_path(
            model,
            pathlib.Path("/cv/OUTPUT_FOLDER/NAME_IN_LOWER_SNAKE_CASE_CV_YEAR.pdf"),
        )
        # Returns: pathlib.Path("/cv/rendercv_output/john_doe_CV_2025.pdf")
        ```

    Args:
        rendercv_model: CV model containing name, date, and output folder for
            substitution.
        file_path: Template path with placeholders.

    Returns:
        Resolved absolute path with substituted placeholders.
    """
    output_folder = rendercv_model.settings.render_command.output_folder
    file_path = resolve_output_folder_placeholder(file_path, output_folder)

    # A value is a part of the file name, whatever it contains (`/` in a name would
    # make a directory), and the same on every operating system:
    placeholders = {
        name: invalid_file_name_characters.sub("_", value)
        for name, value in build_document_placeholders(rendercv_model).items()
    }
    file_name = substitute_placeholders(file_path.name, placeholders)
    resolved_file_path = file_path.parent / file_name
    resolved_file_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_file_path
