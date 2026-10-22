import dataclasses
import pathlib
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any, Unpack

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.cv.cv import connection_fields
from rendercv.schema.models.cv.entry_types import (
    EntryTypeDeclaration,
    parse_entry_type_declarations,
)
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary,
    build_rendercv_model_from_commented_map,
)

from .document import build_document_data, photo_import_path
from .typst_compiler import TypstProject, common_root, read_entry_type_declarations

# The files RenderCV picks up next to a CV's YAML file when they exist.
default_entries_file_name = "entries.typ"
default_design_file_name = "design.typ"


@dataclasses.dataclass(frozen=True, kw_only=True)
class Project:
    """A CV, ready to render: validated, with its entry types and design.

    Why:
        Rendering needs more than the YAML: the entry types it was validated
        against and the Typst files that define them and the design. Keeping
        them together lets every output (PDF, PNG, Markdown, ...) be produced
        from the same state.
    """

    input_file_path: pathlib.Path
    model: RenderCVModel
    entry_types: Mapping[str, EntryTypeDeclaration]
    typst_project: TypstProject
    data: dict[str, Any]


def find_typst_file(
    cli_value: pathlib.Path | None,
    yaml_value: Any,
    input_file_path: pathlib.Path,
    default_name: str,
) -> pathlib.Path | None:
    """Find a design or entries file: from the CLI, the YAML, or by convention.

    Why:
        By convention, `design.typ` and `entries.typ` next to the YAML file are
        used when they exist. Any other file can be chosen with a CLI option
        (relative to the current folder) or in `settings.render_command`
        (relative to the YAML file).

    Args:
        cli_value: The file given on the command line, if any.
        yaml_value: The file given in `settings.render_command`, if any.
        input_file_path: The YAML file.
        default_name: The conventional file name.

    Returns:
        The file's absolute path, or None to use the built-in one.
    """
    if cli_value is not None:
        path = cli_value.absolute()
        if not path.is_file():
            message = f"The file `{cli_value}` doesn't exist."
            raise RenderCVUserError(message)
        return path
    if yaml_value:
        path = input_file_path.parent / str(yaml_value)
        # A missing or non-Typst file is reported by validation instead:
        return path.absolute() if path.is_file() and path.suffix == ".typ" else None
    path = input_file_path.parent / default_name
    return path.absolute() if path.is_file() else None


def resolve_photo(model: RenderCVModel) -> pathlib.Path | None:
    """Return the photo as a local file, downloading it if it's a URL.

    Args:
        model: The validated CV.

    Returns:
        The photo's absolute path, or None if the CV has no photo.
    """
    photo = model.cv.photo
    if photo is None:
        return None
    if isinstance(photo, pathlib.Path):
        return photo.absolute()

    url = str(photo)
    file_name = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name
    if not file_name or "." not in file_name:
        file_name = "photo.jpg"
    output_folder = model.settings.render_command.output_folder
    output_folder.mkdir(parents=True, exist_ok=True)
    destination = output_folder / file_name
    if not destination.exists():
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                destination.write_bytes(response.read())
        except (urllib.error.URLError, OSError) as e:
            message = f"Failed to download the photo from {url}: {e}"
            raise RenderCVUserError(message) from e
    return destination.absolute()


def load_project(
    input_file_path: pathlib.Path,
    *,
    design_file: pathlib.Path | None = None,
    entries_file: pathlib.Path | None = None,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> Project:
    """Read, validate, and prepare a CV for rendering.

    Why:
        Validation depends on Typst: the entry types a CV may use are declared
        in `entries.typ` (or the standard library). So the YAML is read first,
        then the entry types are read from Typst, then the YAML is validated
        against them.

    Args:
        input_file_path: The CV's YAML file.
        design_file: A design file chosen on the command line.
        entries_file: An entries file chosen on the command line.
        kwargs: YAML overlays, output paths, generation flags, and overrides.

    Returns:
        The project, ready to render.
    """
    input_file_path = input_file_path.absolute()
    main_yaml = input_file_path.read_text(encoding="utf-8")
    dictionary, overlay_sources = build_rendercv_dictionary(main_yaml, **kwargs)
    render_command = dictionary["settings"]["render_command"]
    entries_file_path = find_typst_file(
        entries_file,
        render_command.get("entries"),
        input_file_path,
        default_entries_file_name,
    )
    design_file_path = find_typst_file(
        design_file,
        render_command.get("design"),
        input_file_path,
        default_design_file_name,
    )
    font_directories = (input_file_path.parent / "fonts",)
    typst_files = [path for path in (entries_file_path, design_file_path) if path]
    declarations_project = TypstProject(
        root=common_root(input_file_path.parent, *typst_files),
        entries_file_path=entries_file_path,
        font_directories=font_directories,
    )
    entry_types = parse_entry_type_declarations(
        read_entry_type_declarations(declarations_project)
    )
    model = build_rendercv_model_from_commented_map(
        dictionary, input_file_path, overlay_sources, entry_types
    )

    photo = resolve_photo(model)
    typst_project = TypstProject(
        root=common_root(
            input_file_path.parent, *typst_files, *([photo] if photo else [])
        ),
        entries_file_path=entries_file_path,
        design_file_path=design_file_path,
        font_directories=font_directories,
    )
    cv_keys = list((dictionary.get("cv") or {}).keys())
    data = build_document_data(
        model,
        entry_types,
        connection_order=[key for key in cv_keys if key in connection_fields],
        photo=photo_import_path(photo, typst_project.root) if photo else None,
    )
    return Project(
        input_file_path=input_file_path,
        model=model,
        entry_types=entry_types,
        typst_project=typst_project,
        data=data,
    )
