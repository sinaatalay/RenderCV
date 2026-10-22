import json
import pathlib
from collections.abc import Callable

from rendercv.schema.json_schema_generator import (
    generate_json_schema,
    read_standard_entry_types,
)

type RunScript = Callable[..., None]


def test_update_schema(run_script: RunScript, tmp_path: pathlib.Path) -> None:
    run_script("update_schema.py")

    schema = json.loads((tmp_path / "schema.json").read_text(encoding="utf-8"))
    assert schema == generate_json_schema(read_standard_entry_types())
    assert "Sections" in schema["$defs"]
