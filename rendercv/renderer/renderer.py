"""
The `rendercv.renderer.renderer` module contains the necessary functions for rendering
$\\LaTeX$, PDF, Markdown, HTML, and PNG files from the `RenderCVDataModel` object.
"""

import importlib.resources
import pathlib
import re
import shutil
from typing import Optional

import fitz
import markdown
import rendercv_tinytex

from .. import data
from . import templater


def copy_theme_files_to_output_directory(
    theme_name: str,
    output_directory_path: pathlib.Path,
):
    """Copy the auxiliary files (all the files that don't end with `.j2.tex` and `.py`)
    of the theme to the output directory. For example, a theme can have custom
    fonts, and the $\\LaTeX$ needs it. If the theme is a custom theme, then it will be
    copied from the current working directory.

    Args:
        theme_name: The name of the theme.
        output_directory_path: Path to the output directory.
    """
    if theme_name in data.available_themes:
        theme_directory_path = importlib.resources.files(
            f"rendercv.themes.{theme_name}"
        )
    else:
        # Then it means the theme is a custom theme. If theme_directory is not given
        # as an argument, then look for the theme in the current working directory.
        theme_directory_path = pathlib.Path.cwd() / theme_name

        if not theme_directory_path.is_dir():
            message = (
                f"The theme {theme_name} doesn't exist in the available themes and"
                " the current working directory!"
            )
            raise FileNotFoundError(message)

    for theme_file in theme_directory_path.iterdir():
        dont_copy_files_with_these_extensions = [".j2.tex", ".py"]
        # theme_file.suffix returns the latest part of the file name after the last dot.
        # But we need the latest part of the file name after the first dot:
        try:
            suffix = re.search(r"\..*", theme_file.name)[0]  # type: ignore
        except TypeError:
            suffix = ""

        if suffix not in dont_copy_files_with_these_extensions:
            if theme_file.is_dir():
                shutil.copytree(
                    str(theme_file),
                    output_directory_path / theme_file.name,
                    dirs_exist_ok=True,
                )
            else:
                shutil.copyfile(
                    str(theme_file), output_directory_path / theme_file.name
                )


def create_a_latex_file(
    rendercv_data_model: data.RenderCVDataModel, output_directory: pathlib.Path
) -> pathlib.Path:
    """Render the $\\LaTeX$ file with the given data model and write it to the output
    directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory.

    Returns:
        The path to the generated $\\LaTeX$ file.
    """
    # Create output directory if it doesn't exist:
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True)

    jinja2_environment = templater.setup_jinja2_environment()
    latex_file_object = templater.LaTeXFile(
        rendercv_data_model,
        jinja2_environment,
    )

    latex_file_name = f"{str(rendercv_data_model.cv.name).replace(' ', '_')}_CV.tex"
    latex_file_path = output_directory / latex_file_name
    latex_file_object.create_file(latex_file_path)

    return latex_file_path


def create_a_markdown_file(
    rendercv_data_model: data.RenderCVDataModel, output_directory: pathlib.Path
) -> pathlib.Path:
    """Render the Markdown file with the given data model and write it to the output
    directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory.

    Returns:
        The path to the rendered Markdown file.
    """
    # create output directory if it doesn't exist:
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True)

    jinja2_environment = templater.setup_jinja2_environment()
    markdown_file_object = templater.MarkdownFile(
        rendercv_data_model,
        jinja2_environment,
    )

    markdown_file_name = f"{str(rendercv_data_model.cv.name).replace(' ', '_')}_CV.md"
    markdown_file_path = output_directory / markdown_file_name
    markdown_file_object.create_file(markdown_file_path)

    return markdown_file_path


def create_a_latex_file_and_copy_theme_files(
    rendercv_data_model: data.RenderCVDataModel, output_directory: pathlib.Path
) -> pathlib.Path:
    """Render the $\\LaTeX$ file with the given data model in the output directory and
    copy the auxiliary theme files to the output directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory.

    Returns:
        The path to the rendered $\\LaTeX$ file.
    """
    latex_file_path = create_a_latex_file(rendercv_data_model, output_directory)
    copy_theme_files_to_output_directory(
        rendercv_data_model.design.theme, output_directory
    )

    # Copy the profile picture to the output directory, if it exists:
    if rendercv_data_model.cv.photo:
        shutil.copyfile(
            rendercv_data_model.cv.photo,
            output_directory / rendercv_data_model.cv.photo.name,
        )
    return latex_file_path


def render_a_pdf_from_latex(
    latex_file_path: pathlib.Path, local_latex_command: Optional[str] = None
) -> pathlib.Path:
    """Run TinyTeX with the given $\\LaTeX$ file to render the PDF.

    Args:
        latex_file_path: The path to the $\\LaTeX$ file.

    Returns:
        The path to the rendered PDF file.
    """
    return rendercv_tinytex.run_latex(latex_file_path, local_latex_command)


def render_pngs_from_pdf(pdf_file_path: pathlib.Path) -> list[pathlib.Path]:
    """Render a PNG file for each page of the given PDF file.

    Args:
        pdf_file_path: The path to the PDF file.

    Returns:
        The paths to the rendered PNG files.
    """
    # check if the file exists:
    if not pdf_file_path.is_file():
        message = f"The file {pdf_file_path} doesn't exist!"
        raise FileNotFoundError(message)

    # convert the PDF to PNG:
    png_directory = pdf_file_path.parent
    png_file_name = pdf_file_path.stem
    png_files = []
    pdf = fitz.open(pdf_file_path)  # open the PDF file
    for page in pdf:  # iterate the pages
        image = page.get_pixmap(dpi=300)  # type: ignore
        png_file_path = png_directory / f"{png_file_name}_{page.number + 1}.png"  # type: ignore
        image.save(png_file_path)
        png_files.append(png_file_path)

    return png_files


def render_an_html_from_markdown(markdown_file_path: pathlib.Path) -> pathlib.Path:
    """Render an HTML file from a Markdown file with the same name and in the same
    directory. It uses `rendercv/themes/main.j2.html` as the Jinja2 template.

    Args:
        markdown_file_path: The path to the Markdown file.

    Returns:
        The path to the rendered HTML file.
    """
    # check if the file exists:
    if not markdown_file_path.is_file():
        message = f"The file {markdown_file_path} doesn't exist!"
        raise FileNotFoundError(message)

    # Convert the markdown file to HTML:
    markdown_text = markdown_file_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(markdown_text)

    # Get the title of the markdown content:
    title = re.search(r"# (.*)\n", markdown_text)
    title = title.group(1) if title else None

    jinja2_environment = templater.setup_jinja2_environment()
    html_template = jinja2_environment.get_template("main.j2.html")
    html = html_template.render(html_body=html_body, title=title)

    # Write html into a file:
    html_file_path = markdown_file_path.parent / f"{markdown_file_path.stem}.html"
    html_file_path.write_text(html, encoding="utf-8")

    return html_file_path
