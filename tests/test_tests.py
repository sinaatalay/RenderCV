"""Tests that the test folders mirror the folders they test.

Why:
    `tests/` mirrors `src/rendercv/` (`a/b.py` is tested in `tests/a/test_b.py`),
    and `tests/typst/` mirrors the Typst package in `typst/` (`src/entry-type.typ`
    is tested in `tests/typst/src/test_entry_type.py`). Keeping them in sync makes
    the tests of any file easy to find.
"""

import pathlib

import pytest

repository_root = pathlib.Path(__file__).parent.parent
tests_root = repository_root / "tests"
excluded_folders = {"__pycache__", "testdata"}
excluded_files = {"conftest.py", "__init__.py"}


def get_subfolders(folder: pathlib.Path) -> set[str]:
    """Get the names of a folder's subfolders, except caches and test data."""
    return {
        path.name
        for path in folder.iterdir()
        if path.is_dir() and path.name not in excluded_folders
    }


def get_test_file_names(folder: pathlib.Path) -> set[str]:
    """Get the names of a folder's Python files, except `conftest.py`."""
    return {
        path.name
        for path in folder.iterdir()
        if path.is_file() and path.suffix == ".py" and path.name not in excluded_files
    }


def find_mirroring_problems(
    source_root: pathlib.Path,
    test_root: pathlib.Path,
    source_suffix: str,
    *,
    check_root: bool,
) -> list[str]:
    """Find test folders and files that don't mirror a source folder or file.

    Args:
        source_root: The folder that is tested.
        test_root: The folder that mirrors it.
        source_suffix: The suffix of the tested files, like ".py".
        check_root: Whether `test_root` itself may only hold mirrored folders
            and files (`tests/` also holds tests of the whole repository).

    Returns:
        The problems, one per test folder or file.
    """
    source_folders = [
        path.relative_to(source_root)
        for path in source_root.rglob("*")
        if path.is_dir() and not excluded_folders & set(path.parts)
    ]
    if check_root:
        source_folders.append(pathlib.Path())

    problems: list[str] = []
    for folder in source_folders:
        test_folder = test_root / folder
        if not test_folder.is_dir():
            continue
        source_folder = source_root / folder
        display_folder = test_folder.relative_to(repository_root).as_posix()

        for extra_folder in get_subfolders(test_folder) - get_subfolders(source_folder):
            problems.append(f"{display_folder}/{extra_folder}: no such source folder")

        source_names = {
            path.stem.replace("-", "_")
            for path in source_folder.iterdir()
            if path.is_file() and path.suffix == source_suffix
        }
        for test_file in get_test_file_names(test_folder):
            name = test_file.removeprefix("test_").removesuffix(".py")
            if not test_file.startswith("test_") or name not in source_names:
                problems.append(
                    f"{display_folder}/{test_file}: should be `test_<name>.py` for a"
                    f" `<name>{source_suffix}` in"
                    f" {source_folder.relative_to(repository_root).as_posix()}"
                )
    return problems


@pytest.mark.parametrize(
    ("source_root", "test_root", "source_suffix", "check_root"),
    [
        (repository_root / "src" / "rendercv", tests_root, ".py", False),
        (repository_root / "typst", tests_root / "typst", ".typ", True),
    ],
)
def test_tests_mirror_source(
    source_root: pathlib.Path,
    test_root: pathlib.Path,
    source_suffix: str,
    check_root: bool,
) -> None:
    assert source_root.is_dir()

    problems = find_mirroring_problems(
        source_root, test_root, source_suffix, check_root=check_root
    )

    assert not problems, "Tests don't mirror the source:\n" + "\n".join(
        f"  - {problem}" for problem in sorted(problems)
    )
