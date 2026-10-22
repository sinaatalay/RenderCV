import pathlib
from collections.abc import Callable
from typing import Annotated

import rich.panel
import typer
from rich import print

from rendercv.renderer.project import (
    default_design_file_name,
    default_entries_file_name,
)
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_entries_file,
    create_sample_yaml_input_file,
)

from ..app import app
from ..error_handler import handle_user_errors
from .print_welcome import print_welcome

# Written out, because reading them from Typst would slow down every command.
# A test checks that they match `rendercv.designs.names`.
built_in_design_names: tuple[str, ...] = (
    "classic",
    "moderncv",
    "sb2nov",
    "engineeringresumes",
    "engineeringclassic",
    "harvard",
    "ink",
    "ember",
    "opal",
)


@app.command(
    name="new",
    help=(
        "Generate a YAML input file to get started. Example: [yellow]rendercv new"
        ' "John Doe"[/yellow]. Details: [cyan]rendercv new --help[/cyan]'
    ),
)
@handle_user_errors
def cli_command_new(
    full_name: Annotated[str, typer.Argument(help="Your full name")],
    design: Annotated[
        str | None,
        typer.Option(
            help=(
                "Also create a `design.typ` using this built-in design"
                f" ({', '.join(built_in_design_names)}), to change its options or"
                " replace it."
            )
        ),
    ] = None,
    locale: Annotated[
        str,
        typer.Option(
            help=(
                "The language of the CV (available locales are:"
                f" {', '.join(available_locales)}). You can also continue with"
                " `english`, and then write your own `locale` field."
            )
        ),
    ] = "english",
    entries: Annotated[
        bool,
        typer.Option(
            "--entries",
            help=(
                "Also create an `entries.typ` with the standard entry types and an"
                " example of your own entry type."
            ),
        ),
    ] = False,
) -> None:
    print_welcome()

    input_file_path = pathlib.Path(f"{full_name.replace(' ', '_')}_CV.yaml")
    design_file_path = pathlib.Path(default_design_file_name)
    entries_file_path = pathlib.Path(default_entries_file_name)

    # (description, path, contents, whether to create it):
    items_to_create: list[tuple[str, pathlib.Path, Callable[[], str], bool]] = [
        (
            "Your YAML input file",
            input_file_path,
            lambda: create_sample_yaml_input_file(name=full_name, locale=locale),
            True,
        ),
        (
            "Your design",
            design_file_path,
            lambda: create_sample_design_file(design or "classic"),
            design is not None,
        ),
        (
            "Your entry types",
            entries_file_path,
            create_sample_entries_file,
            entries,
        ),
    ]

    # Prepare every file before writing any, so an invalid option creates nothing:
    files_to_write: list[tuple[str, pathlib.Path, str]] = []
    existing_items: list[tuple[str, pathlib.Path]] = []
    for description, path, contents, create in items_to_create:
        if not create:
            continue
        if path.exists():
            existing_items.append((description, path))
        else:
            files_to_write.append((description, path, contents()))

    created_items: list[tuple[str, pathlib.Path]] = []
    for description, path, text in files_to_write:
        path.write_text(text, encoding="utf-8")
        created_items.append((description, path))

    print(build_creation_panel(input_file_path, created_items, existing_items))


def build_creation_panel(
    input_file_path: pathlib.Path,
    created_items: list[tuple[str, pathlib.Path]],
    existing_items: list[tuple[str, pathlib.Path]],
) -> rich.panel.Panel:
    """Build Rich panel summarizing created and existing files.

    Why:
        The ``new`` command output is a structured panel with file statuses and
        next steps. Extracting this keeps the command handler focused on
        orchestration while this function owns presentation.

    Args:
        input_file_path: Path to the generated YAML input file.
        created_items: Items that were newly created (description, path).
        existing_items: Items that already existed (description, path).

    Returns:
        Rich Panel ready for printing.
    """
    lines: list[str] = []

    if any(path == input_file_path for _, path in created_items):
        lines.append(
            "[green]✓[/green] Created your YAML input file: "
            f"[purple]./{input_file_path}[/purple]"
        )
    else:
        lines.append(
            f"Your YAML input file already exists: [purple]./{input_file_path}[/purple]"
        )

    lines.append("")
    lines.append("Next steps:")
    lines.append("  1. Edit the YAML input file with your information")
    lines.append(f"  2. Run: [cyan]rendercv render {input_file_path}[/cyan]")

    created_others = [(d, p) for d, p in created_items if p != input_file_path]
    existing_others = [(d, p) for d, p in existing_items if p != input_file_path]

    if created_others:
        lines.append("")
        lines.append("Also created:")
        for description, path in created_others:
            lines.append(f"  ○ {description}: ./{path}")

    if existing_others:
        lines.append("")
        lines.append("Not modified (already exist):")
        for description, path in existing_others:
            lines.append(f"  - {description}: ./{path}")

    if created_others or existing_others:
        lines.append("")
        lines.append(
            "`design.typ` and `entries.typ` next to your YAML file are used"
            " automatically. Delete them to go back to the built-in ones."
        )

    return rich.panel.Panel(
        "\n".join(lines),
        title="Get started",
        title_align="left",
        border_style="bright_black",
    )
