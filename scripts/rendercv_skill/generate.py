#!/usr/bin/env python3
"""Generate the distributable AI agent skill SKILL.md from a Jinja2 template.

Why:
    The SKILL.md file contains dynamic data (designs, locales, entry types, the
    YAML schema, sample files, design options) that must stay in sync with the
    rendercv package. This script extracts that data and renders the Jinja2
    template to produce an always-current skill file.
"""

import ast
import io
import pathlib
import re
import zipfile

import jinja2
import ruamel.yaml

from rendercv import __version__
from rendercv.schema.json_schema_generator import read_standard_entry_types
from rendercv.schema.models.cv.entry_types import FieldDeclaration
from rendercv.schema.models.cv.social_network import get_available_social_networks
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_entries_file,
    create_sample_yaml_input_file,
    get_built_in_design_names,
)

repository_root = pathlib.Path(__file__).parent.parent.parent
script_directory = pathlib.Path(__file__).parent
template_path = script_directory / "skill_template.j2.md"
output_path = (
    repository_root
    / ".claude"
    / "skills"
    / "rendercv-skill"
    / "skills"
    / "rendercv"
    / "SKILL.md"
)
llms_txt_path = repository_root / "docs" / "llms.txt"
skill_zip_path = repository_root / "docs" / "assets" / "rendercv_skill.zip"
engine_path = repository_root / "typst" / "designs" / "engine.typ"

# Paths to key model source files for dynamic inclusion.
models_dir = repository_root / "src" / "rendercv" / "schema" / "models"

# These source files are included in the skill so agents can see the
# type-safe Pydantic schema of the YAML file's fixed parts. Entries are
# described by the entry type table instead, because their types are Typst.
MODEL_SOURCE_FILES: dict[str, pathlib.Path] = {
    "rendercv_model": models_dir / "rendercv_model.py",
    "cv": models_dir / "cv" / "cv.py",
    "social_network": models_dir / "cv" / "social_network.py",
    "custom_connection": models_dir / "cv" / "custom_connection.py",
    "locale": models_dir / "locale" / "locale.py",
    "settings": models_dir / "settings" / "settings.py",
    "render_command": models_dir / "settings" / "render_command.py",
}


def is_pydantic_model(class_node: ast.ClassDef) -> bool:
    """Check if a class is a Pydantic model, judging by its base classes.

    Why:
        Model files also define dataclasses and helpers (like a social
        network's definition read from its YAML file) that are not part of the
        YAML schema.

    Args:
        class_node: An AST ClassDef node.

    Returns:
        True if a base class name ends with "Model" or "ModelWithoutExtraKeys".
    """
    return any(
        ast.unparse(base).endswith(("BaseModel", "ModelWithoutExtraKeys"))
        for base in class_node.bases
    )


# `pydantic.Field` arguments that only matter for the JSON Schema or the docs:
dropped_field_arguments = {"title", "json_schema_extra", "union_mode"}
# Longer descriptions are left out; the template's prose covers them:
maximum_description_length = 60


def strip_field_arguments(node: ast.AnnAssign) -> ast.AnnAssign:
    """Drop `pydantic.Field` arguments agents don't need from a field.

    Why:
        Titles, JSON Schema extras, and long descriptions (often built from
        f-strings) triple the size of a field without telling an agent anything
        the template doesn't already say.

    Args:
        node: An annotated assignment in a model class.

    Returns:
        The assignment with only the useful `pydantic.Field` arguments.
    """
    call = node.value
    if not isinstance(call, ast.Call) or not ast.unparse(call.func).endswith("Field"):
        return node

    def keep(keyword: ast.keyword) -> bool:
        if keyword.arg in dropped_field_arguments:
            return False
        if keyword.arg == "description":
            return (
                isinstance(keyword.value, ast.Constant)
                and len(str(keyword.value.value)) <= maximum_description_length
            )
        return True

    call.keywords = [keyword for keyword in call.keywords if keep(keyword)]
    return node


def strip_class_body(class_node: ast.ClassDef) -> ast.ClassDef:
    """Strip a class definition down to just field definitions.

    Why:
        Agents need field names, types, and defaults — not validators,
        serializers, or cached properties. Stripping methods removes
        ~50% of tokens from model-heavy files.

    Args:
        class_node: An AST ClassDef node.

    Returns:
        A new ClassDef with only field annotations (no methods).
    """
    new_body: list[ast.stmt] = [
        strip_field_arguments(child)
        for child in class_node.body
        if isinstance(child, ast.AnnAssign)
        and not ast.unparse(child.target).startswith("_")
    ]

    # If the body would be empty, add a `pass` statement
    if not new_body:
        new_body.append(ast.Pass())

    new_class = ast.ClassDef(
        name=class_node.name,
        bases=class_node.bases,
        keywords=class_node.keywords,
        body=new_body,
        decorator_list=[],
    )
    return ast.fix_missing_locations(new_class)


def strip_to_schema(source: str) -> str:
    """Strip a Python source file to only schema-relevant declarations.

    Why:
        Full Pydantic model source files contain imports, validators, helper
        functions, file paths, and regular expressions that are implementation
        internals. Agents only need type aliases and model fields to understand
        the YAML schema.

    Args:
        source: Complete Python source code.

    Returns:
        Stripped source containing only type aliases and Pydantic models.
    """
    tree = ast.parse(source)
    kept_nodes: list[ast.stmt] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.TypeAlias):
            kept_nodes.append(node)
        elif isinstance(node, ast.ClassDef) and is_pydantic_model(node):
            kept_nodes.append(strip_class_body(node))

    return "\n\n".join(ast.unparse(node) for node in kept_nodes).strip() + "\n"


def trim_sample_cv_sections(cv_yaml: str, max_entries: int = 2) -> str:
    """Trim CV sections to at most max_entries entries each.

    Why:
        The sample CV has 5 experience entries, 4 publications, etc. For the
        skill file, showing structure matters more than volume. Trimming to
        2 entries per section saves ~2000 tokens.

    Args:
        cv_yaml: YAML string containing the cv section.
        max_entries: Maximum entries per section.

    Returns:
        Trimmed YAML string.
    """
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    data = yaml.load(cv_yaml)

    sections = data.get("cv", {}).get("sections")
    if sections:
        for section_name in sections:
            entries = sections[section_name]
            if isinstance(entries, list) and len(entries) > max_entries:
                sections[section_name] = entries[:max_entries]

    stream = io.StringIO()
    yaml.dump(data, stream)
    return stream.getvalue()


def describe_field(name: str, field: FieldDeclaration) -> str:
    """Describe an entry type's field for the skill's entry type table.

    Example:
        ```py
        describe_field("authors", FieldDeclaration(kind="list", of="markdown"))
        # "`authors` (list of markdown)"
        ```

    Args:
        name: The field's name.
        field: The field's declaration.

    Returns:
        The field's name and kind.
    """
    kind: str = field.kind
    if field.kind == "list":
        kind = f"list of {field.of or 'markdown'}"
    elif field.kind == "date" and field.allow_text:
        kind = "date or text"
    elif field.kind == "choice":
        kind = "one of " + "/".join(field.choices or ())
    return f"`{name}` ({kind})"


def read_engine_defaults() -> str:
    """Read the design options and their defaults from the classic engine.

    Returns:
        The Typst source of the engine's `defaults` dictionary.
    """
    source = engine_path.read_text(encoding="utf-8")
    match = re.search(r"^#let defaults = \(\n.*?^\)$", source, re.S | re.M)
    if match is None:
        message = f"`#let defaults = (...)` is not in {engine_path}."
        raise ValueError(message)
    return match.group(0)


def build_template_context() -> dict:
    """Assemble all dynamic data for the Jinja2 template.

    Returns:
        Template context dictionary.
    """
    sample_cv = trim_sample_cv_sections(
        create_sample_yaml_input_file(name="John Doe", locale="english")
    )

    entry_types = [
        {
            "name": name,
            "doc": entry_type.doc,
            "required": ", ".join(
                describe_field(field_name, field)
                for field_name, field in entry_type.fields.items()
                if not field.optional
            ),
            "optional": ", ".join(
                describe_field(field_name, field)
                for field_name, field in entry_type.fields.items()
                if field.optional
            )
            or "—",
        }
        for name, entry_type in read_standard_entry_types().items()
    ]

    model_sources: dict[str, str] = {
        name: strip_to_schema(path.read_text(encoding="utf-8"))
        for name, path in MODEL_SOURCE_FILES.items()
    }

    return {
        "version": __version__,
        "available_designs": get_built_in_design_names(),
        "available_locales": available_locales,
        "available_social_networks": get_available_social_networks(),
        "entry_types": entry_types,
        "model_sources": model_sources,
        "sample_cv": sample_cv,
        "sample_design": create_sample_design_file("classic"),
        "sample_entries": create_sample_entries_file(),
        "engine_defaults": read_engine_defaults(),
    }


def generate_skill_file() -> None:
    """Render the Jinja2 template and write SKILL.md, docs/llms.txt, and ZIP."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(script_directory),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    context = build_template_context()

    rendered = template.render(context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    llms_txt_path.write_text(rendered, encoding="utf-8")

    # Generate ZIP for Claude Desktop skill upload
    # Use a fixed timestamp so the zip is reproducible across runs.
    fixed_date = (2025, 1, 1, 0, 0, 0)
    skill_zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(skill_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("rendercv/SKILL.md", date_time=fixed_date)
        zf.writestr(info, rendered)


if __name__ == "__main__":
    generate_skill_file()
    print("Skill generated successfully.")  # NOQA: T201
