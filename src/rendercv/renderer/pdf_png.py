import atexit
import functools
import pathlib
import shutil
import tempfile
import tomllib
from typing import Literal

import rendercv_fonts
import typst

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .typst import copy_photo_next_to_typst_file, render_typst_source


def generate_pdf(
    rendercv_model: RenderCVModel, source: str | None = None
) -> pathlib.Path | None:
    """Compile the Typst source of a CV to PDF, unless disabled.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, if already rendered.

    Returns:
        Path to the PDF file, or None if its generation is disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_pdf:
        return None
    pdf_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.pdf_path
    )
    (pdf,) = compile_typst(rendercv_model, source, "pdf")
    pdf_path.write_bytes(pdf)
    return pdf_path


def generate_png(
    rendercv_model: RenderCVModel, source: str | None = None
) -> list[pathlib.Path] | None:
    """Compile the Typst source of a CV to one PNG file per page, unless disabled.

    Why:
        PNG previews serve web pages and READMEs.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, if already rendered.

    Returns:
        Paths to the PNG files, or None if their generation is disabled.
    """
    command = rendercv_model.settings.render_command
    if command.dont_generate_png:
        return None
    return write_pages(
        compile_typst(rendercv_model, source, "png"),
        resolve_rendercv_file_path(rendercv_model, command.png_path),
    )


def generate_svg(
    rendercv_model: RenderCVModel, source: str | None = None
) -> list[pathlib.Path] | None:
    """Compile the Typst source of a CV to one SVG file per page, unless disabled.

    Why:
        SVG previews are vector images, sharp at any size on web pages.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, if already rendered.

    Returns:
        Paths to the SVG files, or None if their generation is disabled.
    """
    command = rendercv_model.settings.render_command
    if command.dont_generate_svg:
        return None
    return write_pages(
        compile_typst(rendercv_model, source, "svg"),
        resolve_rendercv_file_path(rendercv_model, command.svg_path),
    )


def write_pages(pages: list[bytes], path: pathlib.Path) -> list[pathlib.Path]:
    """Write the pages of a document to numbered files.

    Why:
        The pages of `NAME_CV.png` are `NAME_CV_1.png`, `NAME_CV_2.png`, and so on.
        The pages of a previous render are replaced, so that none is left over from
        a longer CV, and other files are left alone.

    Args:
        pages: The pages.
        path: Path of the document, which the files of its pages are named after.

    Returns:
        Paths to the files of the pages.
    """
    prefix = f"{path.stem}_"
    for existing in path.parent.iterdir():
        if (
            existing.is_file()
            and existing.suffix == path.suffix
            and existing.stem.startswith(prefix)
            and existing.stem.removeprefix(prefix).isdigit()
        ):
            existing.unlink()

    files = []
    for number, page in enumerate(pages, start=1):
        file = path.parent / f"{path.stem}_{number}{path.suffix}"
        file.write_bytes(page)
        files.append(file)
    return files


def compile_typst(
    rendercv_model: RenderCVModel,
    source: str | None,
    output_format: Literal["pdf", "png", "svg"],
) -> list[bytes]:
    """Compile the Typst source of a CV in memory.

    Why:
        The source is compiled as if it were saved: in the directory of the Typst
        file, with the photo next to it. So RenderCV and `typst compile` produce
        the same document from it.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, rendered if None.
        output_format: `"pdf"`, `"png"`, or `"svg"`.

    Returns:
        The compiled document, one item per page for PNG and SVG.
    """
    if source is None:
        source = render_typst_source(rendercv_model)
    directory = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.typst_path
    ).parent
    copy_photo_next_to_typst_file(rendercv_model, directory)
    compiler = get_typst_compiler(rendercv_model._input_file_path, directory)
    standards = rendercv_model.settings.pdf_standards if output_format == "pdf" else []
    result = compiler.compile(
        input=source.encode("utf-8"), format=output_format, pdf_standards=standards
    )
    pages = result if isinstance(result, list) else [result]
    compiled = [page for page in pages if page is not None]
    if len(compiled) != len(pages) or not compiled:
        message = f"Typst returned no {output_format.upper()} output."
        raise RenderCVInternalError(message)
    return compiled


def read_version_from_typst_toml(typst_toml_path: pathlib.Path) -> str:
    """Read the version field from a typst.toml file.

    Why:
        Multiple bundled Typst packages need their version extracted for
        directory layout. Centralizes the parsing logic.

    Args:
        typst_toml_path: Path to the typst.toml file.

    Returns:
        The version string.
    """
    data = tomllib.loads(typst_toml_path.read_text(encoding="utf-8"))
    try:
        return data["package"]["version"]
    except KeyError as e:
        message = f"Could not find version in {typst_toml_path}"
        raise RenderCVInternalError(message) from e


def install_bundled_typst_package(
    bundled_path: pathlib.Path,
    package_name: str,
    temp_dir: pathlib.Path,
    typ_files: list[str],
) -> None:
    """Copy a bundled Typst package into the temporary package cache.

    Why:
        The Typst compiler expects packages in a directory structure of
        preview/{name}/{version}/. This copies the required files from
        a bundled package into that layout.

    Args:
        bundled_path: Path to the bundled package directory.
        package_name: Name of the Typst package (used in directory structure).
        temp_dir: Root of the temporary package cache.
        typ_files: List of .typ filenames to copy alongside typst.toml.
    """
    version = read_version_from_typst_toml(bundled_path / "typst.toml")
    package_directory = temp_dir / "preview" / package_name / version
    package_directory.mkdir(parents=True)
    shutil.copy2(bundled_path / "typst.toml", package_directory / "typst.toml")
    for typ_file in typ_files:
        shutil.copy2(bundled_path / typ_file, package_directory / typ_file)


@functools.lru_cache(maxsize=1)
def get_package_path() -> pathlib.Path:
    """Set up local Typst package resolution from the bundled rendercv package.

    Why:
        The rendercv Typst package is shipped inside the Python package so that
        PDF compilation uses this version of it instead of downloading one from
        Typst Universe. The Typst compiler expects packages in a directory
        structure of preview/{name}/{version}/, so this creates a temporary
        directory with that layout.

    Returns:
        Path to temporary package cache directory.
    """
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-pkg-"))
    atexit.register(shutil.rmtree, str(temp_dir), True)

    renderer_dir = pathlib.Path(__file__).parent

    install_bundled_typst_package(
        bundled_path=renderer_dir / "rendercv_typst",
        package_name="rendercv",
        temp_dir=temp_dir,
        typ_files=["lib.typ"],
    )

    return temp_dir


@functools.lru_cache(maxsize=1)
def get_typst_compiler(
    input_file_path: pathlib.Path | None,
    root: pathlib.Path,
) -> typst.Compiler:
    """Create cached Typst compiler with font paths configured.

    Why:
        Compiler initialization is expensive. Caching enables reuse across
        all compilations. The source file is passed per compile() call, so
        the compiler survives output filename changes (e.g., when cv.name
        changes). Font paths include package fonts and optional user fonts
        from input file directory. The Typst packages that the rendercv package
        imports (fontawesome) are downloaded at build time into the
        typst_packages directory and shipped with RenderCV, so compilation works
        offline; Typst downloads them there itself if they are missing.

    Args:
        input_file_path: Original input file path for relative font resolution.
        root: Root directory for Typst project. Must contain the input file.

    Returns:
        Configured Typst compiler instance.
    """
    return typst.Compiler(
        root=root,
        font_paths=[
            *rendercv_fonts.paths_to_font_folders,
            (
                input_file_path.parent / "fonts"
                if input_file_path
                else pathlib.Path.cwd() / "fonts"
            ),
        ],
        package_path=get_package_path(),
        package_cache_path=pathlib.Path(__file__).parent / "typst_packages",
    )
