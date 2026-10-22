"""Deterministic grader: extract YAML from output, validate with RenderCV's pipeline.

Why:
    Every RenderCV skill response that includes YAML should produce valid,
    schema-compliant YAML. This grader uses RenderCV's own validation (the same
    pipeline as `rendercv render`, with the standard entry types) to catch syntax
    errors and schema violations before the LLM-as-judge even runs. A YAML file
    with RenderCV 2's `design` field fails too.
"""

import functools
import re

from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import EntryTypeDeclaration
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_commented_map,
    read_yaml_with_validation_errors,
)


@functools.cache
def get_standard_entry_types() -> dict[str, EntryTypeDeclaration]:
    """Read the standard entry types from RenderCV's Typst package, once."""
    return read_standard_entry_types()


def extract_yaml_blocks(text: str) -> list[str]:
    """Extract YAML code blocks from markdown output."""
    return re.findall(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)


def get_assert(output: str, context: dict) -> dict:  # noqa: ARG001
    """Validate that output contains a parseable, schema-valid RenderCV YAML block.

    Args:
        output: The LLM's text response.
        context: promptfoo context (required by promptfoo, unused here).

    Returns:
        GradingResult dict with pass, score, and reason.
    """
    yaml_blocks = [block for block in extract_yaml_blocks(output) if "cv:" in block]

    if not yaml_blocks:
        return {
            "pass": False,
            "score": 0,
            "reason": "No RenderCV YAML code block found in output.",
        }

    for i, block in enumerate(yaml_blocks):
        try:
            commented_map = read_yaml_with_validation_errors(block, "main_yaml_file")
            build_rendercv_model_from_commented_map(
                commented_map, entry_types=get_standard_entry_types()
            )
        except RenderCVUserValidationError as e:
            error_messages = "; ".join(err.message for err in e.validation_errors)
            return {
                "pass": False,
                "score": 0,
                "reason": (
                    f"YAML block {i + 1} fails RenderCV validation: {error_messages}"
                ),
            }

    return {
        "pass": True,
        "score": 1,
        "reason": "Valid RenderCV YAML.",
    }
