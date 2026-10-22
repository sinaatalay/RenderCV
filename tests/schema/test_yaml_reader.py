import pathlib

import pytest
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVInternalError, RenderCVUserError
from rendercv.schema.yaml_reader import TypstString, read_yaml


class TestReadYaml:
    def test_reads_a_yaml_file(self, input_file_path: pathlib.Path) -> None:
        result = read_yaml(input_file_path)

        assert isinstance(result, CommentedMap)
        assert result["cv"]["name"] == "John Doe"

    @pytest.mark.parametrize("suffix", [".yml", ".json"])
    def test_reads_other_accepted_extensions(
        self, tmp_path: pathlib.Path, suffix: str
    ) -> None:
        file = tmp_path / f"cv{suffix}"
        file.write_text('{"cv": {"name": "John Doe"}}', encoding="utf-8")

        assert read_yaml(file)["cv"]["name"] == "John Doe"

    def test_reads_yaml_contents_from_a_string(self) -> None:
        result = read_yaml("cv:\n  name: John Doe\n")

        assert result["cv"]["name"] == "John Doe"
        # Coordinates are kept for error messages:
        assert result["cv"].lc.data["name"] == [1, 2, 1, 8]

    def test_rejects_missing_files(self, tmp_path: pathlib.Path) -> None:
        with pytest.raises(RenderCVUserError, match="doesn't exist"):
            read_yaml(tmp_path / "nonexistent.yaml")

    def test_rejects_other_extensions(self, tmp_path: pathlib.Path) -> None:
        file = tmp_path / "cv.txt"
        file.touch()

        with pytest.raises(RenderCVUserError, match="should have one of"):
            read_yaml(file)

    @pytest.mark.parametrize("contents", ["", "# Only a comment\n"])
    def test_rejects_empty_files(self, tmp_path: pathlib.Path, contents: str) -> None:
        file = tmp_path / "empty.yaml"
        file.write_text(contents, encoding="utf-8")

        with pytest.raises(RenderCVUserError, match="empty"):
            read_yaml(file)

    def test_rejects_a_path_passed_as_a_string(self) -> None:
        with pytest.raises(RenderCVInternalError, match=r"pathlib\.Path"):
            read_yaml("plain_string.yaml")

    def test_treats_asterisks_as_text(self) -> None:
        assert read_yaml("key: *not_an_alias")["key"] == "*not_an_alias"

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("2020-01-15", "2020-01-15"), ("2020-01-15 10:00:00", "2020-01-15 10:00:00")],
    )
    def test_keeps_dates_as_text(self, value: str, expected: str) -> None:
        assert read_yaml(f"date: {value}")["date"] == expected


class TestTypstString:
    @pytest.mark.parametrize(
        ("yaml", "expected"),
        [
            ("value: !typst $x^2$", "$x^2$"),
            ('value: !typst "#emph[Hi] - there"', "#emph[Hi] - there"),
            ("value: !typst |\n  line one\n  line two\n", "line one\nline two\n"),
        ],
    )
    def test_typst_tag_makes_a_typst_string(self, yaml: str, expected: str) -> None:
        value = read_yaml(yaml)["value"]

        assert isinstance(value, TypstString)
        assert value == expected

    def test_typst_tag_works_in_lists(self) -> None:
        values = read_yaml("items:\n  - plain\n  - !typst $x$\n")["items"]

        assert [isinstance(value, TypstString) for value in values] == [False, True]
        assert values == ["plain", "$x$"]

    def test_untagged_text_is_a_plain_string(self) -> None:
        assert not isinstance(read_yaml("value: $x^2$")["value"], TypstString)

    def test_typst_tag_only_applies_to_text(self) -> None:
        with pytest.raises(ruamel.yaml.YAMLError):
            read_yaml("value: !typst\n  - a\n")

    def test_is_a_string(self) -> None:
        value = TypstString("#strong[x]")

        assert isinstance(value, str)
        assert value.upper() == "#STRONG[X]"
