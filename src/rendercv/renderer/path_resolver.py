import datetime
import pathlib
import re

from rendercv.schema.models.locale.locale import Locale
from rendercv.schema.models.rendercv_model import RenderCVModel

from .rich_text import markdown_to_rich_text, rich_text_to_plain_text


def build_date_placeholders(date: datetime.date, *, locale: Locale) -> dict[str, str]:
    """Build the date placeholders file names and the PDF title can use.

    Args:
        date: The date.
        locale: The locale, for month names.

    Returns:
        Placeholder names mapped to their values.
    """
    return {
        "MONTH_NAME": locale.month_names[date.month - 1],
        "MONTH_ABBREVIATION": locale.month_abbreviations[date.month - 1],
        "MONTH": str(date.month),
        "MONTH_IN_TWO_DIGITS": f"{date.month:02d}",
        "DAY": str(date.day),
        "DAY_IN_TWO_DIGITS": f"{date.day:02d}",
        "YEAR": str(date.year),
        "YEAR_IN_TWO_DIGITS": f"{date.year % 100:02d}",
    }


def substitute_placeholders(text: str, placeholders: dict[str, str]) -> str:
    """Replace placeholders in text, longest names first.

    Args:
        text: Text with placeholders like `NAME_IN_SNAKE_CASE`.
        placeholders: Placeholder names mapped to their values.

    Returns:
        The text with the placeholders replaced.
    """
    if not placeholders:
        return text
    names = sorted(placeholders, key=lambda name: -len(name))
    # No word boundaries: placeholders sit inside names like `NAME_IN_SNAKE_CASE_CV`.
    pattern = re.compile("|".join(re.escape(name) for name in names))
    return pattern.sub(lambda match: placeholders[match.group(0)], text)


def substitute_date_and_name_placeholders(text: str, model: RenderCVModel) -> str:
    """Replace name and date placeholders, as in file names and the PDF title.

    Args:
        text: Text with placeholders.
        model: The CV, for its name, date, and locale.

    Returns:
        The text with the placeholders replaced.
    """
    current_date = model.settings.resolved_current_date
    placeholders = {
        **build_date_placeholders(current_date, locale=model.locale),
        **build_name_variants(
            rich_text_to_plain_text(markdown_to_rich_text(model.cv.name))
            if model.cv.name
            else None
        ),
        "CURRENT_DATE": (
            f"{model.locale.month_abbreviations[current_date.month - 1]}"
            f" {current_date.year}"
        ),
    }
    return substitute_placeholders(text, placeholders)


def build_name_variants(name: str | None) -> dict[str, str]:
    """Generate all case/separator variants of a name for placeholder substitution.

    Why:
        Output file paths use placeholders like NAME_IN_LOWER_SNAKE_CASE.
        Centralizing variant generation avoids repeating the same
        null-check-and-transform pattern for each variant.

    Args:
        name: The CV owner's name, or None.

    Returns:
        Dictionary mapping placeholder names to their values.
    """
    if name is None:
        return {}
    return {
        "NAME": name,
        "NAME_IN_SNAKE_CASE": name.replace(" ", "_"),
        "NAME_IN_LOWER_SNAKE_CASE": name.replace(" ", "_").lower(),
        "NAME_IN_UPPER_SNAKE_CASE": name.replace(" ", "_").upper(),
        "NAME_IN_KEBAB_CASE": name.replace(" ", "-"),
        "NAME_IN_LOWER_KEBAB_CASE": name.replace(" ", "-").lower(),
        "NAME_IN_UPPER_KEBAB_CASE": name.replace(" ", "-").upper(),
    }


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


def resolve_rendercv_file_path(
    rendercv_model: RenderCVModel, file_path: pathlib.Path
) -> pathlib.Path:
    """Resolve output file path with placeholder substitution and directory creation.

    Why:
        Users specify output paths like ``OUTPUT_FOLDER/NAME_CV_YEAR.pdf`` with
        placeholders for dynamic naming. This function first resolves the
        OUTPUT_FOLDER directory component to the configured output folder, then
        substitutes name and date placeholders in the filename, and finally
        creates parent directories as needed.

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
    file_name = substitute_date_and_name_placeholders(file_path.name, rendercv_model)
    resolved_file_path = file_path.parent / file_name
    resolved_file_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_file_path
