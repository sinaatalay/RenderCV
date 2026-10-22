import datetime
import pathlib
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.renderer.document import build_document_data
from rendercv.renderer.project import load_project
from rendercv.renderer.typst_compiler import TypstProject, query_typst
from rendercv.renderer.typst_packages import source_typst_package_directory
from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import EntryTypeDeclaration
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_commented_map,
)
from rendercv.schema.sample_generator import create_sample_yaml_input_file

type TypstValue = Callable[..., Any]
type TypstText = Callable[..., str]
type RenderedWords = Callable[..., list[tuple[str, str]]]
type CvData = Callable[..., dict[str, Any]]

value_label = "rendercv-test-value"
word_label = "rendercv-test-word"
pinned_current_date = datetime.date(2025, 6, 1)


def content_to_text(value: Any) -> str:
    """Flatten Typst content, as a query returns it in JSON, to its text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(content_to_text(item) for item in value)
    if not isinstance(value, dict):
        return str(value)
    func = value.get("func")
    if func == "space":
        return " "
    if func in ("linebreak", "parbreak"):
        return "\n"
    if "text" in value:
        return value["text"]
    for key in ("children", "body", "child"):
        if key in value:
            return content_to_text(value[key])
    return ""


@pytest.fixture(scope="session")
def package_project() -> TypstProject:
    """A Typst project rooted in the package, so tests can import its files."""
    return TypstProject(root=source_typst_package_directory)


@pytest.fixture(scope="session")
def typst_value(package_project: TypstProject) -> TypstValue:
    """Evaluate a Typst expression and return its value as JSON.

    The expression may use `rendercv` (the package), `data`, and whatever the
    prelude defines, e.g. `#import "/src/dates.typ": *` for the package's
    internals. Errors are raised as `RenderCVUserError`.
    """

    def evaluate(
        expression: str, *, prelude: str = "", data: dict[str, Any] | None = None
    ) -> Any:
        body = f"{prelude}\n#metadata({expression}) <{value_label}>"
        return query_typst(package_project, body, value_label, data)

    return evaluate


@pytest.fixture(scope="session")
def typst_text(typst_value: TypstValue) -> TypstText:
    """Evaluate a Typst expression and return the text of the content."""

    def evaluate(
        expression: str, *, prelude: str = "", data: dict[str, Any] | None = None
    ) -> str:
        return content_to_text(typst_value(expression, prelude=prelude, data=data))

    return evaluate


@pytest.fixture(scope="session")
def rendered_words(package_project: TypstProject) -> RenderedWords:
    """Render a CV and read back its laid out words and their font weights.

    Why:
        Designs draw some parts only while laying out the page (like header
        connections), so their text isn't in the content `render` returns.
        Recording every word as it's laid out also shows how it's styled.
    """

    def render(
        data: dict[str, Any],
        *,
        design: str = "rendercv.base-design",
        types: str = "all-types",
        prelude: str = "",
    ) -> list[tuple[str, str]]:
        body = (
            f"{prelude}\n"
            '#show regex("\\\\S+"): it => [#context [#metadata((it.text,'
            f" repr(text.weight))) <{word_label}>]#it]\n"
            f"#rendercv.render(data, types: {types}, design: {design})\n"
            f"#context [#metadata(query(<{word_label}>).map(word => word.value))"
            f" <{value_label}>]"
        )
        return [
            (word, weight.strip('"'))
            for word, weight in query_typst(package_project, body, value_label, data)
        ]

    return render


@pytest.fixture(scope="session")
def standard_entry_types() -> dict[str, EntryTypeDeclaration]:
    return read_standard_entry_types()


@pytest.fixture(scope="session")
def cv_data(standard_entry_types: dict[str, EntryTypeDeclaration]) -> CvData:
    """Build RenderCV's data from a `cv` mapping, as RenderCV sends it."""

    def build(cv: dict[str, Any], **top_level: Any) -> dict[str, Any]:
        settings = {
            "current_date": pinned_current_date,
            **top_level.pop("settings", {}),
        }
        model = build_rendercv_model_from_commented_map(
            {"cv": cv, "settings": settings, **top_level},
            entry_types=standard_entry_types,
        )
        return build_document_data(
            model, standard_entry_types, connection_order=list(cv)
        )

    return build


@pytest.fixture(scope="session")
def sample_data(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """The data of the sample CV. Copy it before changing it."""
    input_file_path: pathlib.Path = tmp_path_factory.mktemp("sample") / "cv.yaml"
    input_file_path.write_text(
        create_sample_yaml_input_file()
        + f"settings:\n  current_date: {pinned_current_date.isoformat()}\n",
        encoding="utf-8",
    )
    return load_project(input_file_path).data
