import functools
import json
import pathlib

from rendercv import __version__
from rendercv.exception import RenderCVUserError
from rendercv.renderer.typst_compiler import TypstProject, query_typst
from rendercv.renderer.typst_packages import get_rendercv_typst_version

from .models.locale.locale import available_locales

sample_content_path = pathlib.Path(__file__).parent / "sample_content.yaml"


@functools.cache
def get_built_in_design_names() -> tuple[str, ...]:
    """Read the names of the built-in designs from the Typst package.

    Returns:
        The design names.
    """
    project = TypstProject(root=pathlib.Path.cwd())
    return tuple(
        query_typst(
            project,
            "#metadata(rendercv.designs.names) <rendercv-design-names>",
            "rendercv-design-names",
        )
    )


def create_sample_yaml_input_file(
    *, name: str = "John Doe", locale: str = "english"
) -> str:
    """Write a sample CV to start from.

    Why:
        `rendercv new` gives users a CV that renders right away and shows every
        standard entry type, so they learn by editing.

    Args:
        name: The person's full name.
        locale: The CV's language.

    Returns:
        The YAML.
    """
    if locale not in available_locales:
        message = (
            f"The locale `{locale}` is not built in. Built-in locales:"
            f" {', '.join(available_locales)}. You can also start with `english`"
            " and write your own `locale` in the YAML file."
        )
        raise RenderCVUserError(message)
    content = sample_content_path.read_text(encoding="utf-8")
    # Drop the repository-relative schema comment:
    content = content.split("\n", 1)[1]
    content = content.replace("  name: John Doe\n", f"  name: {json.dumps(name)}\n", 1)
    schema_comment = (
        "# yaml-language-server:"
        f" $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v{__version__}/schema.json\n"
    )
    return schema_comment + content + f"locale:\n  language: {locale}\n"


def create_sample_design_file(design: str) -> str:
    """Write a `design.typ` that uses a built-in design.

    Args:
        design: The built-in design's name.

    Returns:
        The Typst source.
    """
    design_names = get_built_in_design_names()
    if design not in design_names:
        message = (
            f"There is no built-in design `{design}`. Built-in designs:"
            f" {', '.join(design_names)}."
        )
        raise RenderCVUserError(message)
    return f"""// The design of your CV. To use another design, replace `{design}` with one of:
// {", ".join(design_names)}.
#import "@preview/rendercv:{get_rendercv_typst_version()}": designs

#let design = designs.{design}(
  // Change any option, for example:
  // page: (size: "a4"),
  // colors: (name: rgb("#004f90"), section_titles: rgb("#004f90")),
  // typography: (font_family: "Source Sans 3", font_size: (body: 10pt)),
)
"""


def create_sample_entries_file() -> str:
    """Write an `entries.typ` with the standard entry types and an example.

    Returns:
        The Typst source.
    """
    return f"""// The entry types your CV can use: the standard ones, plus your own.
#import "@preview/rendercv:{get_rendercv_typst_version()}": *

// An example of your own entry type: a talk. In the YAML, an entry with
// `title`, `event`, and `date` is now a talk.
#let talk = entry-type(
  doc: "A talk at a conference or event.",
  fields: (
    title: field("markdown", doc: "The title of the talk."),
    event: field("markdown", doc: "Where the talk was given."),
    date: field("date", doc: "When the talk was given."),
    slides: field("url", optional: true, doc: "A link to the slides."),
  ),
  // Drawn as a normal entry, so every design styles it:
  look: (it, ctx) => as-entry(
    "normal",
    name: [#it.title -- #emph(it.event)],
    date: it.date,
    summary: if it.slides != none [#link(it.slides)[Slides]],
  ),
)
"""
