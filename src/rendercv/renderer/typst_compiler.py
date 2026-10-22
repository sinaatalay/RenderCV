import dataclasses
import functools
import json
import os
import pathlib
import re
from typing import Any, Literal, cast

import typst

from rendercv.exception import RenderCVUserError

from .typst_packages import (
    add_version_aliases,
    get_package_path,
    get_rendercv_typst_version,
)

type OutputFormat = Literal["pdf", "png", "svg", "html"]

data_input_name = "rendercv-data"
# A place in a file in Typst's error reports, like "┌─ design.typ:3:14":
diagnostic_span_pattern = re.compile(
    r"┌─ (?P<path>.+?):(?P<line>\d+):(?P<column>\d+)$", re.MULTILINE
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TypstProject:
    """The Typst side of a CV: which entry types and design it uses, and where.

    Why:
        Entry types and the design are Typst files next to the CV (or the
        built-in ones). Typst only reads files inside one root folder, so the
        root is the common folder of everything it needs to read.
    """

    root: pathlib.Path
    entries_file_path: pathlib.Path | None = None
    design_file_path: pathlib.Path | None = None
    font_directories: tuple[pathlib.Path, ...] = ()

    @functools.cached_property
    def typst_files(self) -> list[pathlib.Path]:
        """The user's Typst files."""
        return [
            path
            for path in (self.entries_file_path, self.design_file_path)
            if path is not None
        ]


def common_root(*paths: pathlib.Path) -> pathlib.Path:
    """Find the deepest folder containing all the given files and folders.

    Args:
        paths: Absolute paths.

    Returns:
        Their common folder.
    """
    return pathlib.Path(os.path.commonpath([str(path) for path in paths]))


def import_path(project: TypstProject, path: pathlib.Path) -> str:
    """Write a path the way a file at the Typst root imports it.

    Args:
        project: The Typst project.
        path: An absolute path inside the project's root.

    Returns:
        The path relative to the root, starting with "/".
    """
    return "/" + path.relative_to(project.root).as_posix()


def build_main_source(project: TypstProject, body: str) -> str:
    """Build the main Typst file that loads the entry types and the design.

    Why:
        The main file only imports: RenderCV's Typst package, the entry types,
        and the design. The CV's content reaches Typst as JSON data, never as
        generated code, so no user text can break the document.

    Args:
        project: The Typst project.
        body: Typst code using `rendercv`, `types`, and `design`.

    Returns:
        The main file's source.
    """
    version = get_rendercv_typst_version()
    lines = [f'#import "@preview/rendercv:{version}" as rendercv']
    if project.entries_file_path is not None:
        lines.append(
            f'#import "{import_path(project, project.entries_file_path)}" as entries'
        )
        lines.append("#let types = rendercv.collect-entry-types(dictionary(entries))")
    else:
        lines.append("#let types = rendercv.collect-entry-types(dictionary(rendercv))")
    # Hand-overs may target standard entry types the user's file doesn't export:
    lines.append(
        "#let all-types = rendercv.collect-entry-types(dictionary(rendercv)) + types"
    )
    if project.design_file_path is not None:
        lines.append(
            f'#import "{import_path(project, project.design_file_path)}" as design-file'
        )
        lines.append(
            '#let design = if "design" in dictionary(design-file) { design-file.design }'
            ' else { panic("The design file must define `design`, e.g. `#let design ='
            ' designs.classic()`.") }'
        )
    else:
        lines.append("#let design = rendercv.designs.classic()")
    lines.append(
        f"#let data = json(bytes(sys.inputs.at({json.dumps(data_input_name)})))"
    )
    lines.append(body)
    return "\n".join(lines) + "\n"


document_body = """#let photo = if data.header.photo == none { none } else {
  read(data.header.photo, encoding: none)
}
#rendercv.render(data + (header: data.header + (photo: photo)), types: all-types, design: design)"""

markdown_body = """#metadata(rendercv.to-markdown-document(
  rendercv.render(data + (header: data.header + (photo: none)), types: all-types, design: rendercv.base-design),
  plain: {plain},
)) <rendercv-markdown>"""

declarations_body = "#metadata(rendercv.declarations(types)) <rendercv-declarations>"


def get_bundled_font_directories() -> list[pathlib.Path]:
    """Return the font folders of `rendercv-fonts`, if it's installed.

    Why:
        The fonts the built-in designs use come in the separate
        `rendercv-fonts` package, so the core package stays small (for example
        in the browser). Without it, Typst falls back to its own fonts.

    Returns:
        The font folders, or an empty list.
    """
    try:
        import rendercv_fonts  # noqa: PLC0415
    except ImportError:
        return []
    return [pathlib.Path(path) for path in rendercv_fonts.paths_to_font_folders]


# Scanned fonts, by font folders and the files in them:
fonts_cache: dict[
    tuple[tuple[pathlib.Path, ...], tuple[tuple[str, int], ...]], typst.Fonts
] = {}


def get_fonts(font_directories: tuple[pathlib.Path, ...]) -> typst.Fonts:
    """Scan the fonts Typst may use, once until the font files change.

    Why:
        Scanning fonts reads every font file, which takes a noticeable part of
        a render, especially in the browser. The scanned fonts are shared by
        every compilation and query, and scanned again only when a font file
        is added, removed, or changed (for example in watch mode).

    Args:
        font_directories: Folders with fonts, besides RenderCV's own fonts.

    Returns:
        The fonts: RenderCV's, the given folders', Typst's embedded ones, and
        the system's.
    """
    directories = (*get_bundled_font_directories(), *font_directories)
    files = tuple(
        (str(file), file.stat().st_mtime_ns)
        for directory in directories
        if directory.is_dir()
        for file in sorted(directory.rglob("*"))
        if file.is_file()
    )
    key = (directories, files)
    if key not in fonts_cache:
        fonts_cache[key] = typst.Fonts(font_paths=list(directories))
    return fonts_cache[key]


@functools.cache
def get_compiler(root: pathlib.Path, fonts: typst.Fonts) -> typst.Compiler:
    """Create a Typst compiler, once per root and fonts.

    Why:
        Keeping the compiler makes recompiling after an edit fast, because
        Typst reuses its work from the previous compilation.

    Args:
        root: The folder Typst may read files from.
        fonts: The fonts Typst may use.

    Returns:
        The compiler.
    """
    return typst.Compiler(root=root, font_paths=fonts, package_path=get_package_path())


def find_user_file_location(
    diagnostic: str, root: pathlib.Path | None = None
) -> str | None:
    """Find where in the user's own Typst files an error happened.

    Why:
        Typst reports every place an error passed through: RenderCV's package,
        the in-memory main file, and the user's `design.typ` or `entries.typ`.
        Only the user's files are worth pointing at; the first of them is the
        closest to the error.

    Args:
        diagnostic: Typst's full error report.
        root: The Typst project's root. Typst writes paths relative to the
            current folder; paths inside the root are written relative to it
            instead, so they don't depend on where RenderCV runs.

    Returns:
        The location, like "`design.typ`, line 3, column 14", or None if the
        error didn't pass through a user file.
    """
    for match in diagnostic_span_pattern.finditer(diagnostic):
        path = match.group("path")
        # RenderCV's packages, and the in-memory main file:
        if path.startswith("@") or pathlib.PurePath(path).name.startswith("__typst_py"):
            continue
        if root is not None:
            absolute_path = (pathlib.Path.cwd() / path).resolve()
            if absolute_path.is_relative_to(root.resolve()):
                path = absolute_path.relative_to(root.resolve()).as_posix()
        return f"`{path}`, line {match.group('line')}, column {match.group('column')}"
    return None


def typst_error_to_user_error(
    error: RuntimeError, root: pathlib.Path | None = None
) -> RenderCVUserError:
    """Turn a Typst error into an error RenderCV shows the user.

    Args:
        error: The Typst error. Querying reports errors as plain
            `RuntimeError`s without hints or locations.
        root: The Typst project's root, to write file paths relative to.

    Returns:
        A user error with Typst's message, where it happened, and hints.
    """
    message = str(getattr(error, "message", None) or error)
    message = message.removeprefix("failed to compile document: ")
    message = message.removeprefix("panicked with: ")
    text = f"Typst couldn't compile the CV: {message}"
    diagnostic = getattr(error, "diagnostic", None)
    location = (
        find_user_file_location(diagnostic, root)
        if isinstance(diagnostic, str)
        else None
    )
    if location is not None:
        text += f"\n\nIn {location}."
    hints = [str(hint) for hint in getattr(error, "hints", None) or []]
    if hints:
        text += "\n\n" + "\n".join(f"Hint: {hint}" for hint in hints)
    return RenderCVUserError(text)


def compile_typst(
    project: TypstProject,
    body: str,
    data: dict[str, Any],
    output_format: OutputFormat,
) -> bytes | list[bytes]:
    """Compile a main file with the CV's data.

    Args:
        project: The Typst project.
        body: Typst code using `rendercv`, `types`, `design`, and `data`.
        data: The CV's data.
        output_format: The output format.

    Returns:
        The output: one file, or one image per page for PNG and SVG.
    """
    add_version_aliases(project.typst_files)
    compiler = get_compiler(project.root, get_fonts(project.font_directories))
    try:
        # Only compiling to an output file returns None:
        return cast(
            bytes | list[bytes],
            compiler.compile(
                input=build_main_source(project, body).encode(),
                format=output_format,
                sys_inputs={data_input_name: json.dumps(data)},
            ),
        )
    except typst.TypstError as e:
        raise typst_error_to_user_error(e, project.root) from e


def query_typst(
    project: TypstProject, body: str, label: str, data: dict[str, Any] | None = None
) -> Any:
    """Run a main file and read back the value of a labeled `metadata`.

    Args:
        project: The Typst project.
        body: Typst code producing `#metadata(...) <label>`.
        label: The label, without angle brackets.
        data: The CV's data, if the body uses it.

    Returns:
        The metadata's value, decoded from JSON.
    """
    add_version_aliases(project.typst_files)
    package_path = get_package_path()
    compiler = typst.Compiler(
        input=build_main_source(project, body).encode(),
        root=project.root,
        font_paths=get_fonts(project.font_directories),
        package_path=package_path,
        sys_inputs={data_input_name: json.dumps(data or {})},
    )
    try:
        return json.loads(compiler.query(f"<{label}>", field="value", one=True))
    # typst-py's query raises plain RuntimeErrors, not TypstErrors:
    except RuntimeError as e:
        query_error = e
    # Those have no location, so compile once more to get a TypstError that has:
    try:
        compiler.compile(format="pdf")
    except typst.TypstError as e:
        raise typst_error_to_user_error(e, project.root) from query_error
    raise typst_error_to_user_error(query_error, project.root) from query_error


def read_entry_type_declarations(project: TypstProject) -> dict[str, Any]:
    """Read which entry types exist and what fields they have from Typst.

    Args:
        project: The Typst project.

    Returns:
        Entry type names mapped to their declarations, as JSON.
    """
    return query_typst(project, declarations_body, "rendercv-declarations")


def render_markdown(project: TypstProject, data: dict[str, Any], *, plain: bool) -> str:
    """Render the CV as Markdown or plain text, from the same entry type looks.

    Args:
        project: The Typst project.
        data: The CV's data.
        plain: Whether to write plain text instead of Markdown.

    Returns:
        The Markdown or plain text.
    """
    body = markdown_body.replace("{plain}", "true" if plain else "false")
    return query_typst(project, body, "rendercv-markdown", data)
