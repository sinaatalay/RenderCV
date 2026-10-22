"""Render and validate CVs from code, without the command line.

The npm package uses this module to run RenderCV in Pyodide, and it works the
same in regular Python:

```py
import pathlib

from rendercv.api import render

cv = render(pathlib.Path("John_Doe_CV.yaml"), formats=("pdf", "markdown"))
pathlib.Path("cv.pdf").write_bytes(cv.pdf)
```

Nothing is written next to the YAML file; the outputs are returned. Like the
command line, `design.typ` and `entries.typ` next to the YAML file are used
if they exist.
"""

import dataclasses
import pathlib
from collections.abc import Sequence
from typing import Literal, Unpack

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    YamlSource,
)
from rendercv.renderer.outputs import (
    build_html,
    build_markdown,
    build_pdf,
    build_pngs,
    build_svgs,
    build_typst_source,
)
from rendercv.renderer.project import load_project
from rendercv.schema.rendercv_model_builder import BuildRendercvModelArguments

type OutputFormat = Literal["pdf", "png", "svg", "html", "markdown", "typst"]
type ProblemSource = Literal["input", "locale", "settings"]

available_output_formats: tuple[OutputFormat, ...] = OutputFormat.__value__.__args__

yaml_source_names: dict[YamlSource, ProblemSource] = {
    "main_yaml_file": "input",
    "locale_yaml_file": "locale",
    "settings_yaml_file": "settings",
}


@dataclasses.dataclass(frozen=True, kw_only=True)
class Problem:
    """Something wrong with a CV's input, and where it is.

    Why:
        Editors show problems next to the text that causes them, so each
        problem carries the file it's in and its line and column, not just a
        message.
    """

    message: str
    # The YAML file the problem is in: the input file, or a locale or settings
    # overlay. None for problems that aren't in a YAML file (Typst errors say
    # where they are in their message).
    source: ProblemSource | None = None
    # The keys leading to the problem, like ("cv", "sections", "education", "0").
    path: tuple[str, ...] = ()
    # Where the problem is in `source`, counting from 1:
    line: int | None = None
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class RenderedCV:
    """The outputs of a render. Formats that weren't asked for are None."""

    pdf: bytes | None = None
    # One image per page:
    png: tuple[bytes, ...] | None = None
    svg: tuple[str, ...] | None = None
    html: str | None = None
    markdown: str | None = None
    # The Typst source, which compiles on its own:
    typst: str | None = None


def problems_from_error(
    error: RenderCVUserError | RenderCVUserValidationError,
) -> list[Problem]:
    """Turn an error RenderCV raises for bad input into problems.

    Args:
        error: The error.

    Returns:
        The problems, with their places in the YAML where known.
    """
    if isinstance(error, RenderCVUserError):
        return [Problem(message=str(error.message or error))]
    problems: list[Problem] = []
    for validation_error in error.validation_errors:
        start, end = validation_error.yaml_location or ((None, None), (None, None))
        problems.append(
            Problem(
                message=validation_error.message,
                source=yaml_source_names[validation_error.yaml_source],
                path=tuple(str(key) for key in validation_error.schema_location or ()),
                line=start[0],
                column=start[1],
                end_line=end[0],
                end_column=end[1],
            )
        )
    return problems


def validate(
    input_file_path: pathlib.Path,
    *,
    design_file: pathlib.Path | None = None,
    entries_file: pathlib.Path | None = None,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> list[Problem]:
    """Check a CV without rendering it.

    Args:
        input_file_path: The CV's YAML file.
        design_file: A design file to use instead of `design.typ`.
        entries_file: An entries file to use instead of `entries.typ`.
        kwargs: YAML overlays and overrides, as for the command line.

    Returns:
        The problems; empty if the CV is valid.
    """
    try:
        load_project(
            input_file_path,
            design_file=design_file,
            entries_file=entries_file,
            **kwargs,
        )
    except (RenderCVUserError, RenderCVUserValidationError) as e:
        return problems_from_error(e)
    return []


def render(
    input_file_path: pathlib.Path,
    *,
    formats: Sequence[OutputFormat] = ("pdf",),
    design_file: pathlib.Path | None = None,
    entries_file: pathlib.Path | None = None,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> RenderedCV:
    """Render a CV to the given formats.

    Args:
        input_file_path: The CV's YAML file.
        formats: The formats to render to.
        design_file: A design file to use instead of `design.typ`.
        entries_file: An entries file to use instead of `entries.typ`.
        kwargs: YAML overlays and overrides, as for the command line.

    Returns:
        The outputs.

    Raises:
        RenderCVUserValidationError: If the YAML is invalid.
        RenderCVUserError: If anything else about the input is wrong, like an
            error in a Typst file. `problems_from_error` turns both into
            problems.
    """
    unknown_formats = [
        output_format
        for output_format in formats
        if output_format not in available_output_formats
    ]
    if unknown_formats:
        message = (
            f"Unknown output formats: {', '.join(unknown_formats)}. Available"
            f" formats: {', '.join(available_output_formats)}."
        )
        raise RenderCVUserError(message)
    project = load_project(
        input_file_path,
        design_file=design_file,
        entries_file=entries_file,
        **kwargs,
    )
    return RenderedCV(
        pdf=build_pdf(project) if "pdf" in formats else None,
        png=tuple(build_pngs(project)) if "png" in formats else None,
        svg=tuple(build_svgs(project)) if "svg" in formats else None,
        html=build_html(project) if "html" in formats else None,
        markdown=build_markdown(project) if "markdown" in formats else None,
        typst=build_typst_source(project) if "typst" in formats else None,
    )
