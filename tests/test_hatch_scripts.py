import subprocess

import pytest


@pytest.mark.parametrize(
    "script_name",
    [
        "format",
        "lint",
        "check-types",
        "precommit",
        "update-schema",
        "update-examples",
        "create-executable",
        "docs:build",
        "docs:update-entry-figures",
    ],
)
def test_default_format(script_name):
    # Check if hatch is installed:
    try:
        subprocess.run(["hatch", "--version"], check=True)
        subprocess.run(["hatch", "run", script_name], check=True)
    except FileNotFoundError:
        pass
