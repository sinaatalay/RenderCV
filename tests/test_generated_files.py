"""Tests that auto-generated files are up to date with the source code.

Why:
    Several files in the repository (schema.json, the examples, SKILL.md,
    llms.txt) are derived from source code. These tests fail when the committed
    files diverge from what the generation code produces, catching staleness on
    every PR instead of silently regenerating in CI.
"""

import json
import pathlib
import subprocess
import sys

import pytest

from rendercv import __version__
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_yaml_input_file,
    get_built_in_design_names,
)

repository_root = pathlib.Path(__file__).parent.parent
examples_folder = repository_root / "examples"


def run_just(recipe: str) -> None:
    """Run a just recipe and raise on failure."""
    subprocess.run(
        ["just", recipe],
        cwd=repository_root,
        check=True,
        capture_output=True,
    )


@pytest.mark.skipif(
    sys.platform == "win32", reason="Schema generation differs on Windows"
)
def test_schema_json_is_up_to_date() -> None:
    schema_path = repository_root / "schema.json"
    before = schema_path.read_text(encoding="utf-8")

    run_just("update-schema")

    after = schema_path.read_text(encoding="utf-8")
    # Restore original content
    schema_path.write_text(before, encoding="utf-8")

    assert before == after, (
        "schema.json is stale. Run `just update-schema` to regenerate."
    )


def test_examples_have_one_folder_per_built_in_design() -> None:
    folders = {path.name for path in examples_folder.iterdir() if path.is_dir()}

    assert folders == set(get_built_in_design_names()), (
        "examples/ is stale. Run `just update-examples` to regenerate."
    )


@pytest.mark.parametrize("design", get_built_in_design_names())
def test_example_is_up_to_date(design: str) -> None:
    folder = examples_folder / design
    yaml = (folder / "John_Doe_CV.yaml").read_text(encoding="utf-8")
    design_typ = (folder / "design.typ").read_text(encoding="utf-8")

    message = f"examples/{design} is stale. Run `just update-examples` to regenerate."
    assert yaml == create_sample_yaml_input_file(name="John Doe", locale="english"), (
        message
    )
    assert design_typ == create_sample_design_file(design), message
    assert (folder / "John_Doe_CV.pdf").is_file(), message


def test_npm_package_version_is_up_to_date() -> None:
    """The npm package runs this version of RenderCV, so it has its version."""
    js_folder = repository_root / "js"
    package_json = json.loads((js_folder / "package.json").read_text(encoding="utf-8"))
    version_ts = (js_folder / "src" / "version.ts").read_text(encoding="utf-8")

    assert package_json["version"] == __version__, (
        "js/package.json is stale. Run `just build-js` to update it."
    )
    assert f'export const version = "{__version__}";' in version_ts, (
        "js/src/version.ts is stale. Run `just build-js` to update it."
    )


def test_skill_md_is_up_to_date() -> None:
    skill_path = (
        repository_root
        / ".claude"
        / "skills"
        / "rendercv-skill"
        / "skills"
        / "rendercv"
        / "SKILL.md"
    )
    before = skill_path.read_text(encoding="utf-8")

    llms_txt_path = repository_root / "docs" / "llms.txt"
    llms_before = llms_txt_path.read_text(encoding="utf-8")

    run_just("update-skill")

    skill_after = skill_path.read_text(encoding="utf-8")
    llms_after = llms_txt_path.read_text(encoding="utf-8")

    # Restore original content
    skill_path.write_text(before, encoding="utf-8")
    llms_txt_path.write_text(llms_before, encoding="utf-8")

    assert before == skill_after, (
        "skills/rendercv/SKILL.md is stale. Run `just update-skill` to regenerate."
    )
    assert llms_before == llms_after, (
        "docs/llms.txt is stale. Run `just update-skill` to regenerate."
    )
