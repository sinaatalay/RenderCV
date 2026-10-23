"""Tests that auto-generated files are up to date with the source code.

Why:
    Several files in the repository (schema.json, example YAMLs, SKILL.md,
    llms.txt) are derived from source code. These tests fail when the committed
    files diverge from what the generation code produces, catching staleness on
    every PR instead of silently regenerating in CI.
"""

import pathlib
import subprocess

import pytest

from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.sample_generator import create_sample_yaml_input_file

repository_root = pathlib.Path(__file__).parent.parent


def run_just(recipe: str) -> None:
    """Run a just recipe and raise on failure."""
    subprocess.run(
        ["just", recipe],
        cwd=repository_root,
        check=True,
        capture_output=True,
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


@pytest.mark.parametrize("theme", available_themes)
def test_example_yaml_is_up_to_date(theme: str) -> None:
    yaml_path = (
        repository_root / "examples" / f"John_Doe_{theme.capitalize()}Theme_CV.yaml"
    )
    before = yaml_path.read_text(encoding="utf-8")

    expected = create_sample_yaml_input_file(
        file_path=None,
        name="John Doe",
        theme=theme,
        locale="english",
    )

    assert before == expected, (
        f"examples/John_Doe_{theme.capitalize()}Theme_CV.yaml is stale. "
        "Run `just update-examples` to regenerate."
    )


skill_path = repository_root / "skills" / "rendercv" / "SKILL.md"


def test_skill_is_up_to_date() -> None:
    generated_files = [
        skill_path,
        repository_root / "skills" / "README.md",
        repository_root / "docs" / "llms.txt",
    ]
    before = [path.read_text(encoding="utf-8") for path in generated_files]

    run_just("update-skill")

    after = [path.read_text(encoding="utf-8") for path in generated_files]
    # Restore original content
    for path, content in zip(generated_files, before, strict=True):
        path.write_text(content, encoding="utf-8")

    for path, old, new in zip(generated_files, before, after, strict=True):
        assert old == new, (
            f"{path.relative_to(repository_root)} is stale. Run `just update-skill`"
            " to regenerate."
        )


def test_skill_lists_every_available_theme() -> None:
    skill = skill_path.read_text(encoding="utf-8")

    for theme in available_themes:
        assert f"`{theme}`" in skill


def test_skill_has_no_repository_relative_schema_paths() -> None:
    assert "$schema=../" not in skill_path.read_text(encoding="utf-8")
