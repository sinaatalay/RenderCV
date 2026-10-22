import pathlib
from typing import Annotated

import typer

from rendercv.exception import RenderCVUserError
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
)

from ..app import app
from ..error_handler import handle_user_errors
from .parse_override_arguments import parse_override_arguments
from .progress_panel import ProgressPanel
from .run_rendercv import collect_input_file_paths, run_rendercv
from .watcher import run_function_if_files_change


@app.command(
    name="render",
    help=(
        "Render a YAML input file. Example: [yellow]rendercv render"
        " John_Doe_CV.yaml[/yellow]. Details: [cyan]rendercv render --help[/cyan]"
    ),
    # allow extra arguments for updating the old_data model (for overriding the values of
    # the input file):
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
@handle_user_errors
def cli_command_render(
    input_file_name: Annotated[
        pathlib.Path, typer.Argument(help="The YAML input file.")
    ],
    output_folder: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--output-folder",
            "-o",
            help=(
                "Base output folder for all generated files. Replaces the default"
                " 'rendercv_output' folder."
            ),
        ),
    ] = None,
    design: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--design",
            "-d",
            help=(
                "The Typst file that defines the design. The default is"
                " `design.typ` next to the YAML file, if it exists."
            ),
        ),
    ] = None,
    entries: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--entries",
            "-e",
            help=(
                "The Typst file that defines the entry types. The default is"
                " `entries.typ` next to the YAML file, if it exists."
            ),
        ),
    ] = None,
    locale: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--locale-catalog",
            "-lc",
            help='The "locale" field\'s YAML input file.',
        ),
    ] = None,
    settings: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--settings",
            "-s",
            help='The "settings" field\'s YAML input file.',
        ),
    ] = None,
    typst_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--typst-path",
            "-typ",
            help=(
                "Save the generated Typst file to the specified path, relative to the"
                " input file."
            ),
        ),
    ] = None,
    pdf_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--pdf-path",
            "-pdf",
            help=(
                "Save the generated PDF file to the specified path, relative to the"
                " input file."
            ),
        ),
    ] = None,
    markdown_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--markdown-path",
            "-md",
            help=(
                "Save the generated Markdown file to the specified path, relative to"
                " the input file."
            ),
        ),
    ] = None,
    html_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--html-path",
            "-html",
            help=(
                "Save the generated HTML file to the specified path, relative to the"
                " input file."
            ),
        ),
    ] = None,
    png_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--png-path",
            "-png",
            help=(
                "Save the generated PNG files to the specified path, relative to the"
                " input file."
            ),
        ),
    ] = None,
    dont_generate_markdown: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-markdown",
            "-nomd",
            help=("If provided, the Markdown file will not be generated."),
        ),
    ] = None,
    dont_generate_html: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-html",
            "-nohtml",
            help="If provided, the HTML file will not be generated.",
        ),
    ] = None,
    dont_generate_typst: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-typst",
            "-notyp",
            help=(
                "If provided, the Typst source file will not be written. PDF and PNG"
                " files are still generated."
            ),
        ),
    ] = None,
    dont_generate_pdf: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-pdf",
            "-nopdf",
            help="If provided, the PDF file will not be generated.",
        ),
    ] = None,
    dont_generate_png: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-png",
            "-nopng",
            help="If provided, the PNG file will not be generated.",
        ),
    ] = None,
    watch: Annotated[
        bool | None,
        typer.Option(
            "--watch",
            "-w",
            help=(
                "If provided, RenderCV will automatically re-run when the input file is"
                " updated."
            ),
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="If provided, RenderCV will not print any messages.",
        ),
    ] = False,
    # Dummy argument that only exists to show the override syntax in --help:
    yaml_field_override: Annotated[  # noqa: ARG001
        str | None,
        typer.Option(
            "--YAMLLOCATION",
            help="Overrides the value of YAMLLOCATION. For example,"
            ' [cyan bold]--cv.phone "123-456-7890"[/cyan bold].',
        ),
    ] = None,
    extra_data_model_override_arguments: typer.Context = None,  # ty: ignore[invalid-parameter-default]
) -> None:
    input_file_path = pathlib.Path(input_file_name).absolute()
    if not input_file_path.is_file():
        message = f"The input file `{input_file_name}` doesn't exist."
        raise RenderCVUserError(message)
    for option, path in (("--design", design), ("--entries", entries)):
        if path is not None and path.suffix != ".typ":
            message = (
                f"`{option} {path}`: this should be a Typst file (`.typ`). Designs"
                " and entry types are written in Typst since RenderCV 3. To convert"
                " a RenderCV 2 design, run `rendercv migrate` on the YAML file that"
                " has it."
            )
            raise RenderCVUserError(message)

    arguments: BuildRendercvModelArguments = {
        "output_folder": output_folder,
        "typst_path": typst_path,
        "pdf_path": pdf_path,
        "markdown_path": markdown_path,
        "html_path": html_path,
        "png_path": png_path,
        "dont_generate_typst": dont_generate_typst,
        "dont_generate_html": dont_generate_html,
        "dont_generate_markdown": dont_generate_markdown,
        "dont_generate_pdf": dont_generate_pdf,
        "dont_generate_png": dont_generate_png,
        "overrides": parse_override_arguments(extra_data_model_override_arguments),
    }
    with ProgressPanel(quiet=quiet) as progress_panel:

        def render() -> None:
            run_rendercv(
                input_file_path,
                progress_panel,
                design=design,
                entries=entries,
                locale=locale,
                settings=settings,
                **arguments,
            )

        if watch:
            run_function_if_files_change(
                lambda: list(
                    collect_input_file_paths(
                        input_file_path,
                        design=design,
                        entries=entries,
                        locale=locale,
                        settings=settings,
                    ).values()
                ),
                render,
            )
        else:
            render()
