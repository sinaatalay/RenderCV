import io
import pathlib
import shutil
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.project import (
    Project,
    default_design_file_name,
    default_entries_file_name,
    find_typst_file,
    load_project,
    resolve_photo,
)
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.models.rendercv_model import RenderCVModel

type LoadCv = Callable[..., Project]
type BuildModel = Callable[..., RenderCVModel]

version = get_rendercv_typst_version()
profile_picture = pathlib.Path(__file__).parent / "testdata" / "profile_picture.jpg"

talk_entries = f"""#import "@preview/rendercv:{version}": entry-type, field, as-entry
#let talk = entry-type(
  fields: (title: field("markdown"), event: field("markdown")),
  look: (it, ctx) => as-entry("normal", name: [#it.title at #it.event]),
)
"""


def design_source(design: str) -> str:
    return (
        f'#import "@preview/rendercv:{version}": designs\n'
        f"#let design = designs.{design}()\n"
    )


class TestFindTypstFile:
    @pytest.fixture
    def input_file_path(self, tmp_path: pathlib.Path) -> pathlib.Path:
        for name in ("design.typ", "cli.typ", "yaml.typ", "notes.yaml"):
            (tmp_path / name).write_text("", encoding="utf-8")
        return tmp_path / "cv.yaml"

    def test_prefers_the_command_line(
        self,
        input_file_path: pathlib.Path,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)

        path = find_typst_file(
            pathlib.Path("cli.typ"), "yaml.typ", input_file_path, "design.typ"
        )

        assert path == tmp_path / "cli.typ"
        assert path is not None
        assert path.is_absolute()

    def test_uses_the_yaml_setting_relative_to_the_yaml_file(
        self,
        input_file_path: pathlib.Path,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path.parent)

        path = find_typst_file(None, "yaml.typ", input_file_path, "design.typ")

        assert path == tmp_path / "yaml.typ"

    def test_uses_the_conventional_file(self, input_file_path: pathlib.Path) -> None:
        path = find_typst_file(None, None, input_file_path, "design.typ")

        assert path == input_file_path.parent / "design.typ"

    def test_returns_none_without_any_file(self, input_file_path: pathlib.Path) -> None:
        assert find_typst_file(None, None, input_file_path, "entries.typ") is None

    @pytest.mark.parametrize("yaml_value", ["missing.typ", "notes.yaml"])
    def test_leaves_invalid_yaml_settings_to_validation(
        self, input_file_path: pathlib.Path, yaml_value: str
    ) -> None:
        assert find_typst_file(None, yaml_value, input_file_path, "design.typ") is None

    def test_raises_for_a_missing_command_line_file(
        self, input_file_path: pathlib.Path
    ) -> None:
        with pytest.raises(
            RenderCVUserError, match=r"^The file `missing.typ` doesn't exist\.$"
        ):
            find_typst_file(
                pathlib.Path("missing.typ"), None, input_file_path, "design.typ"
            )


class TestResolvePhoto:
    @pytest.fixture
    def downloads(self, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        downloaded: list[str] = []

        def urlopen(url: str, timeout: float) -> io.BytesIO:
            assert timeout > 0
            downloaded.append(url)
            return io.BytesIO(b"image bytes")

        monkeypatch.setattr(urllib.request, "urlopen", urlopen)
        return downloaded

    def build_model_with_photo(
        self, build_model: BuildModel, tmp_path: pathlib.Path, photo: str
    ) -> RenderCVModel:
        return build_model(
            {"photo": photo},
            settings={"render_command": {"output_folder": str(tmp_path / "output")}},
        )

    def test_returns_none_without_a_photo(self, build_model: BuildModel) -> None:
        assert resolve_photo(build_model({})) is None

    def test_returns_a_local_photo(self, build_model: BuildModel) -> None:
        model = build_model({"photo": str(profile_picture)})

        assert resolve_photo(model) == profile_picture

    @pytest.mark.parametrize(
        ("url", "file_name"),
        [
            ("https://example.com/images/me.png", "me.png"),
            ("https://example.com/me.jpg?size=large", "me.jpg"),
            ("https://example.com/avatar", "photo.jpg"),
            ("https://example.com/", "photo.jpg"),
        ],
    )
    def test_downloads_a_photo_url(
        self,
        build_model: BuildModel,
        tmp_path: pathlib.Path,
        downloads: list[str],
        url: str,
        file_name: str,
    ) -> None:
        model = self.build_model_with_photo(build_model, tmp_path, url)

        photo = resolve_photo(model)

        assert photo == tmp_path / "output" / file_name
        assert photo is not None
        assert photo.read_bytes() == b"image bytes"
        assert downloads == [url]

    def test_downloads_a_photo_only_once(
        self, build_model: BuildModel, tmp_path: pathlib.Path, downloads: list[str]
    ) -> None:
        model = self.build_model_with_photo(
            build_model, tmp_path, "https://example.com/me.png"
        )

        resolve_photo(model)
        resolve_photo(model)

        assert len(downloads) == 1

    def test_raises_if_the_download_fails(
        self,
        build_model: BuildModel,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def urlopen(*arguments: object, **keyword_arguments: object) -> Any:
            raise urllib.error.URLError("no internet")

        monkeypatch.setattr(urllib.request, "urlopen", urlopen)
        model = self.build_model_with_photo(
            build_model, tmp_path, "https://example.com/me.png"
        )

        with pytest.raises(
            RenderCVUserError,
            match=r"^Failed to download the photo from https://example\.com/me\.png:",
        ):
            resolve_photo(model)


class TestLoadProject:
    def test_loads_the_sample_cv(self, sample_project: Project) -> None:
        assert sample_project.input_file_path.name == "cv.yaml"
        assert sample_project.input_file_path.is_absolute()
        assert sample_project.model.cv.name == "John Doe"
        assert "experience" in sample_project.entry_types
        assert sample_project.typst_project.root == (
            sample_project.input_file_path.parent
        )
        assert sample_project.typst_project.entries_file_path is None
        assert sample_project.typst_project.design_file_path is None
        assert sample_project.typst_project.font_directories == (
            sample_project.input_file_path.parent / "fonts",
        )
        assert sample_project.data["header"]["plain_name"] == "John Doe"

    def test_orders_connections_like_the_yaml(self, load_cv: LoadCv) -> None:
        project = load_cv(
            "cv:\n"
            "  name: Jane Doe\n"
            "  website: https://jane.dev\n"
            "  email: jane@doe.com\n"
            "  location: Istanbul\n"
        )

        assert [c["kind"] for c in project.data["header"]["connections"]] == [
            "website",
            "email",
            "location",
        ]

    def test_uses_entries_and_design_next_to_the_yaml(self, load_cv: LoadCv) -> None:
        project = load_cv(
            "cv:\n"
            "  sections:\n"
            "    talks:\n"
            "      - title: Typst for CVs\n"
            "        event: TypstConf\n",
            files={
                default_entries_file_name: talk_entries,
                default_design_file_name: design_source("sb2nov"),
            },
        )

        assert list(project.entry_types) == ["talk"]
        assert project.data["sections"][0]["entries"] == [
            {
                "type": "talk",
                "fields": {"title": ["Typst for CVs"], "event": ["TypstConf"]},
            }
        ]
        assert project.typst_project.entries_file_path == (
            project.input_file_path.parent / "entries.typ"
        )
        assert project.typst_project.design_file_path == (
            project.input_file_path.parent / "design.typ"
        )

    def test_validates_against_the_entry_types_of_the_entries_file(
        self, load_cv: LoadCv
    ) -> None:
        with pytest.raises(RenderCVUserValidationError):
            load_cv(
                "cv:\n  sections:\n    skills:\n      - label: A\n        details: B\n",
                files={default_entries_file_name: talk_entries},
            )

    def test_uses_files_chosen_in_the_yaml(
        self, load_cv: LoadCv, tmp_path: pathlib.Path
    ) -> None:
        project = load_cv(
            "cv:\n  name: Jane Doe\n"
            "settings:\n"
            "  render_command:\n"
            "    design: typst/my-design.typ\n"
            "    entries: typst/my-entries.typ\n",
            files={
                "typst/my-design.typ": design_source("moderncv"),
                "typst/my-entries.typ": talk_entries,
                default_design_file_name: design_source("sb2nov"),
            },
        )

        assert project.typst_project.design_file_path == (
            tmp_path / "typst" / "my-design.typ"
        )
        assert project.typst_project.entries_file_path == (
            tmp_path / "typst" / "my-entries.typ"
        )
        assert list(project.entry_types) == ["talk"]

    def test_uses_files_chosen_on_the_command_line(
        self,
        load_cv: LoadCv,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        other_folder = tmp_path.parent / f"{tmp_path.name}-designs"
        other_folder.mkdir()
        (other_folder / "harvard.typ").write_text(
            design_source("harvard"), encoding="utf-8"
        )
        monkeypatch.chdir(other_folder)

        project = load_cv(
            "cv:\n  name: Jane Doe\n",
            files={default_design_file_name: design_source("sb2nov")},
            design_file=pathlib.Path("harvard.typ"),
        )

        assert project.typst_project.design_file_path == other_folder / "harvard.typ"
        # Typst can only read files in its root:
        assert project.typst_project.root == tmp_path.parent

    def test_puts_the_photo_inside_the_typst_root(
        self, load_cv: LoadCv, tmp_path: pathlib.Path
    ) -> None:
        shutil.copy(profile_picture, tmp_path / "me.jpg")

        project = load_cv("cv:\n  name: Jane Doe\n  photo: me.jpg\n")

        assert project.data["header"]["photo"] == "/me.jpg"
        assert project.typst_project.root == tmp_path

    def test_passes_overrides(self, load_cv: LoadCv, tmp_path: pathlib.Path) -> None:
        project = load_cv(
            "cv:\n  name: Jane Doe\n",
            overrides={"cv.name": "John Doe"},
            output_folder=str(tmp_path / "out"),
            dont_generate_png=True,
        )

        assert project.model.cv.name == "John Doe"
        assert project.model.settings.render_command.output_folder == tmp_path / "out"
        assert project.model.settings.render_command.dont_generate_png

    def test_raises_for_errors_in_the_entries_file(self, load_cv: LoadCv) -> None:
        with pytest.raises(RenderCVUserError, match="unclosed delimiter"):
            load_cv(
                "cv:\n  name: Jane Doe\n",
                files={default_entries_file_name: "#let talk = (\n"},
            )

    def test_reads_the_yaml_from_any_file_name(self, tmp_path: pathlib.Path) -> None:
        input_file_path = tmp_path / "Jane_CV.yml"
        input_file_path.write_text("cv:\n  name: Jane Doe\n", encoding="utf-8")

        project = load_project(input_file_path)

        assert project.input_file_path == input_file_path
        assert project.data["header"]["plain_name"] == "Jane Doe"
