import io
import pathlib
import shutil
from typing import Annotated, Any

import rich.panel
import ruamel.yaml
import typer
from rich import print
from ruamel.yaml.comments import CommentedMap, TaggedScalar

from rendercv.exception import RenderCVUserError
from rendercv.renderer.project import default_design_file_name
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.v2_migration import migrate_design

from ..app import app
from ..error_handler import handle_user_errors


@app.command(
    name="migrate",
    help=(
        "Move a RenderCV 2 YAML file's design into a `design.typ`. Example:"
        " [yellow]rendercv migrate John_Doe_CV.yaml[/yellow]."
    ),
)
@handle_user_errors
def cli_command_migrate(
    input_file_name: Annotated[
        pathlib.Path, typer.Argument(help="The RenderCV 2 YAML input file.")
    ],
) -> None:
    input_file_path = input_file_name.absolute()
    if not input_file_path.is_file():
        message = f"The file `{input_file_name}` doesn't exist."
        raise RenderCVUserError(message)

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    source = input_file_path.read_text(encoding="utf-8")
    document = load_yaml_mapping(yaml, source, input_file_name)

    # The keys to remove from the YAML file, as (mapping, key):
    removals: list[tuple[CommentedMap, str]] = []
    design: Any = None
    if "design" in document:
        design = document["design"] or {}
        removals.append((document, "design"))
    settings = document.get("settings")
    render_command = (
        settings.get("render_command") if isinstance(settings, CommentedMap) else None
    )
    design_file = (
        render_command.get("design")
        if isinstance(render_command, CommentedMap)
        else None
    )
    if isinstance(render_command, CommentedMap) and str(design_file).endswith(
        (".yaml", ".yml")
    ):
        # Like in RenderCV 2, a design file overrides the `design` field:
        design_file_path = input_file_path.parent / str(design_file)
        if not design_file_path.is_file():
            message = f"The design file `{design_file}` doesn't exist."
            raise RenderCVUserError(message)
        design_document = load_yaml_mapping(
            yaml,
            design_file_path.read_text(encoding="utf-8"),
            pathlib.Path(str(design_file)),
        )
        design = design_document.get("design") or {}
        removals.append((render_command, "design"))
    if design is None:
        message = "This file has no `design` field to migrate."
        raise RenderCVUserError(message)

    design_path = input_file_path.parent / default_design_file_name
    if design_path.exists():
        message = f"`{design_path.name}` already exists. Move it away and run again."
        raise RenderCVUserError(message)

    migration = migrate_design(design, version=get_rendercv_typst_version())
    design_path.write_text(migration.source, encoding="utf-8")

    backup_path = input_file_path.with_suffix(".v2" + input_file_path.suffix)
    shutil.copyfile(input_file_path, backup_path)
    input_file_path.write_text(
        remove_yaml_keys(yaml, source, document, removals), encoding="utf-8"
    )

    lines = [
        f"[green]✓[/green] Created [purple]{design_path.name}[/purple] from the"
        " `design` field.",
        f"[green]✓[/green] Removed the `design` field from [purple]{input_file_path.name}"
        f"[/purple] (the original is in [purple]{backup_path.name}[/purple]).",
    ]
    if migration.warnings:
        lines += ["", "Couldn't convert:"] + [
            f"  - {warning}" for warning in migration.warnings
        ]
    lines += ["", f"Next: [cyan]rendercv render {input_file_name}[/cyan]"]
    print(
        rich.panel.Panel(
            "\n".join(lines),
            title="Migrated to RenderCV 3",
            title_align="left",
            border_style="bright_black",
        )
    )


def load_yaml_mapping(
    yaml: ruamel.yaml.YAML, source: str, file_name: pathlib.Path
) -> CommentedMap:
    """Read a YAML file that should be a mapping, like a RenderCV input file.

    Args:
        yaml: The round-trip YAML reader.
        source: The file's contents.
        file_name: The file's name, for error messages.

    Returns:
        The mapping, with its comments and line numbers.
    """
    try:
        document = yaml.load(source)
    except ruamel.yaml.YAMLError as e:
        message = f"`{file_name}` is not a valid YAML file: {e}"
        raise RenderCVUserError(message) from e
    return document if isinstance(document, CommentedMap) else CommentedMap()


def remove_yaml_key(source: str, line: int) -> str:
    """Remove a YAML key's line and the lines nested under it.

    Why:
        Dumping the YAML again would reformat the user's whole file (its
        indentation and line wrapping). Removing only the key's lines keeps
        everything else exactly as the user wrote it.

    Args:
        source: The YAML file's contents.
        line: The key's line, starting from 0.

    Returns:
        The YAML without the key.
    """
    lines = source.splitlines(keepends=True)
    key_indentation = len(lines[line]) - len(lines[line].lstrip())
    end = line + 1
    while end < len(lines):
        text = lines[end]
        if text.strip() and len(text) - len(text.lstrip()) <= key_indentation:
            break
        end += 1
    return "".join(lines[:line] + lines[end:])


def plain_yaml_data(data: Any) -> Any:
    """Turn round-trip YAML data into plain data that can be compared.

    Args:
        data: Data read by a round-trip YAML reader.

    Returns:
        The same data as lists and tuples, in the same order, with each scalar's
        type.
    """
    if isinstance(data, dict):
        # A mapping whose keys were all removed reads back as null:
        return [
            (plain_yaml_data(key), plain_yaml_data(value))
            for key, value in data.items()
        ] or None
    if isinstance(data, list):
        return [plain_yaml_data(item) for item in data]
    if isinstance(data, TaggedScalar):
        return (str(data.tag), data.value)
    if data is None:
        return None
    return (type(data).__name__, data)


def remove_yaml_keys(
    yaml: ruamel.yaml.YAML,
    source: str,
    document: CommentedMap,
    removals: list[tuple[CommentedMap, str]],
) -> str:
    """Remove keys from a YAML file, keeping the rest of it as it is.

    Why:
        Block-style YAML (what RenderCV files use) can be edited line by line,
        which keeps comments and formatting. For anything else, like flow-style
        mappings, the YAML is dumped again instead.

    Args:
        yaml: The round-trip YAML reader.
        source: The YAML file's contents.
        document: The file, as read by `yaml`.
        removals: The keys to remove, as (mapping, key).

    Returns:
        The YAML without the keys.
    """
    lines = sorted((mapping.lc.key(key)[0] for mapping, key in removals), reverse=True)
    for mapping, key in removals:
        del mapping[key]

    edited = source
    for line in lines:
        edited = remove_yaml_key(edited, line)

    try:
        if plain_yaml_data(yaml.load(edited)) == plain_yaml_data(document):
            return edited
    except ruamel.yaml.YAMLError:
        pass
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    output = io.StringIO()
    yaml.dump(document, output)
    return output.getvalue()
