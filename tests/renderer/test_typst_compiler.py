import datetime
import pathlib
import sys

import pytest
import typst
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVUserError
from rendercv.renderer.document import build_document_data
from rendercv.renderer.project import Project
from rendercv.renderer.typst_compiler import (
    TypstProject,
    build_main_source,
    common_root,
    compile_typst,
    data_input_name,
    declarations_body,
    document_body,
    find_user_file_location,
    get_bundled_font_directories,
    get_compiler,
    get_fonts,
    import_path,
    query_typst,
    read_entry_type_declarations,
    render_markdown,
    typst_error_to_user_error,
)
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.models.cv.entry_types import EntryTypeDeclaration
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_commented_map,
)

version = get_rendercv_typst_version()

standard_entry_type_names = [
    "normal",
    "experience",
    "education",
    "publication",
    "one_line",
    "bullet",
    "numbered",
    "reversed_numbered",
    "paragraph",
]


def test_typst_project(tmp_path: pathlib.Path) -> None:
    entries = tmp_path / "entries.typ"
    design = tmp_path / "design.typ"

    assert TypstProject(root=tmp_path).typst_files == []
    assert TypstProject(root=tmp_path, design_file_path=design).typst_files == [design]
    assert TypstProject(
        root=tmp_path, entries_file_path=entries, design_file_path=design
    ).typst_files == [entries, design]


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (["/a/b/cv.yaml"], "/a/b/cv.yaml"),
        (["/a/b", "/a/b/design.typ"], "/a/b"),
        (["/a/b", "/a/c/design.typ"], "/a"),
        (["/a/b", "/a/b/c/entries.typ", "/a/b/photo.jpg"], "/a/b"),
        (["/a/b", "/x/design.typ"], "/"),
    ],
)
def test_common_root(paths: list[str], expected: str) -> None:
    assert common_root(*(pathlib.Path(path) for path in paths)) == pathlib.Path(
        expected
    )


@pytest.mark.parametrize(
    ("relative_path", "expected"),
    [
        ("design.typ", "/design.typ"),
        ("typst/entries.typ", "/typst/entries.typ"),
        ("a b/ü.typ", "/a b/ü.typ"),
    ],
)
def test_import_path(tmp_path: pathlib.Path, relative_path: str, expected: str) -> None:
    project = TypstProject(root=tmp_path)

    assert import_path(project, tmp_path / relative_path) == expected


class TestBuildMainSource:
    def test_uses_the_standard_types_and_the_classic_design(
        self, tmp_path: pathlib.Path
    ) -> None:
        source = build_main_source(TypstProject(root=tmp_path), "BODY")

        assert source == (
            f'#import "@preview/rendercv:{version}" as rendercv\n'
            "#let types = rendercv.collect-entry-types(dictionary(rendercv))\n"
            "#let all-types = rendercv.collect-entry-types(dictionary(rendercv))"
            " + types\n"
            "#let design = rendercv.designs.classic()\n"
            f'#let data = json(bytes(sys.inputs.at("{data_input_name}")))\n'
            "BODY\n"
        )

    def test_imports_the_entries_and_design_files(self, tmp_path: pathlib.Path) -> None:
        project = TypstProject(
            root=tmp_path,
            entries_file_path=tmp_path / "typst" / "entries.typ",
            design_file_path=tmp_path / "design.typ",
        )

        source = build_main_source(project, "BODY")

        assert '#import "/typst/entries.typ" as entries\n' in source
        assert (
            "#let types = rendercv.collect-entry-types(dictionary(entries))\n" in source
        )
        assert '#import "/design.typ" as design-file\n' in source
        assert "design-file.design" in source
        assert "rendercv.designs.classic()" not in source
        assert source.endswith("BODY\n")

    def test_uses_the_design_of_the_design_file(self, tmp_path: pathlib.Path) -> None:
        design_file = tmp_path / "design.typ"
        design_file.write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            '#let design = designs.sb2nov(page: (size: "a4"))\n',
            encoding="utf-8",
        )
        project = TypstProject(root=tmp_path, design_file_path=design_file)

        value = query_typst(
            project,
            "#metadata((design.name, design.options.page.size)) <value>",
            "value",
        )

        assert value == ["sb2nov", "a4"]

    def test_explains_a_design_file_without_design(
        self, tmp_path: pathlib.Path
    ) -> None:
        design_file = tmp_path / "design.typ"
        design_file.write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            "#let my-design = designs.classic()\n",
            encoding="utf-8",
        )
        project = TypstProject(root=tmp_path, design_file_path=design_file)

        with pytest.raises(
            RenderCVUserError, match="The design file must define `design`"
        ):
            compile_typst(project, document_body, {}, "pdf")


class TestTypstErrorToUserError:
    def test_includes_the_message_and_hints(self) -> None:
        with pytest.raises(typst.TypstError) as error:
            typst.compile(b"$ab$")

        user_error = typst_error_to_user_error(error.value)

        assert user_error.message == (
            "Typst couldn't compile the CV: unknown variable: ab\n\n"
            "Hint: if you meant to display multiple letters as is, try adding"
            " spaces between each letter: `a b`\n"
            "Hint: or if you meant to display this as text, try placing it in"
            ' quotes: `"ab"`'
        )

    def test_reads_plain_runtime_errors_of_queries(self) -> None:
        user_error = typst_error_to_user_error(
            RuntimeError("failed to compile document: something broke")
        )

        assert user_error.message == "Typst couldn't compile the CV: something broke"


class TestGetBundledFontDirectories:
    def test_returns_the_folders_of_rendercv_fonts(self) -> None:
        directories = get_bundled_font_directories()

        assert directories
        assert all(directory.is_dir() for directory in directories)

    def test_returns_nothing_without_rendercv_fonts(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(sys.modules, "rendercv_fonts", None)

        assert get_bundled_font_directories() == []


def test_get_compiler(tmp_path: pathlib.Path) -> None:
    fonts = get_fonts(())
    compiler = get_compiler(tmp_path, fonts)

    assert compiler is get_compiler(tmp_path, fonts)
    assert compiler is not get_compiler(tmp_path, get_fonts((tmp_path,)))


class TestGetFonts:
    def test_scans_fonts_once(self, tmp_path: pathlib.Path) -> None:
        assert get_fonts((tmp_path,)) is get_fonts((tmp_path,))

    def test_scans_again_when_a_font_file_changes(self, tmp_path: pathlib.Path) -> None:
        fonts = get_fonts((tmp_path,))
        (tmp_path / "new-font.ttf").write_bytes(b"not really a font")

        assert get_fonts((tmp_path,)) is not fonts

    def test_includes_the_given_folders(self, tmp_path: pathlib.Path) -> None:
        bundled_font = next(
            file
            for folder in get_bundled_font_directories()
            for file in sorted(folder.glob("*.ttf"))
        )
        font = tmp_path / "copy.ttf"
        font.write_bytes(bundled_font.read_bytes())

        paths = {info.path for info in get_fonts((tmp_path,)).fonts()}

        assert str(font) in paths


class TestCompileTypst:
    @pytest.mark.parametrize(
        ("output_format", "signature"),
        [("pdf", b"%PDF"), ("html", b"<!DOCTYPE html>")],
    )
    def test_compiles_to_one_file(
        self, sample_project: Project, output_format: str, signature: bytes
    ) -> None:
        output = compile_typst(
            sample_project.typst_project,
            document_body,
            sample_project.data,
            output_format,  # ty: ignore[invalid-argument-type]
        )

        assert isinstance(output, bytes)
        assert output.startswith(signature)

    @pytest.mark.parametrize(
        ("output_format", "signature"),
        [("png", b"\x89PNG"), ("svg", b"<svg")],
    )
    def test_compiles_to_one_file_per_page(
        self, sample_project: Project, output_format: str, signature: bytes
    ) -> None:
        pages = compile_typst(
            sample_project.typst_project,
            document_body,
            sample_project.data,
            output_format,  # ty: ignore[invalid-argument-type]
        )

        assert isinstance(pages, list)
        assert len(pages) == 2
        assert all(page.startswith(signature) for page in pages)

    def test_raises_user_errors(self, tmp_path: pathlib.Path) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"^Typst couldn't compile the CV: boom$",
        ):
            compile_typst(TypstProject(root=tmp_path), '#panic("boom")', {}, "pdf")

    def test_passes_the_data(self, tmp_path: pathlib.Path) -> None:
        html = compile_typst(
            TypstProject(root=tmp_path),
            "#data.greeting",
            {"greeting": "Hi #1 $2"},
            "html",
        )

        assert isinstance(html, bytes)
        assert b"Hi #1 $2" in html

    @settings(max_examples=25, deadline=None)
    @given(
        texts=st.lists(
            st.text(
                alphabet=st.characters(exclude_categories=["Cs"]),
                min_size=1,
                max_size=30,
            ).filter(lambda text: text.strip() != ""),
            min_size=5,
            max_size=5,
        ),
        bold_keywords=st.lists(st.text(max_size=5), max_size=2),
    )
    def test_hostile_text_never_breaks_compilation(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        standard_entry_types: dict[str, EntryTypeDeclaration],
        texts: list[str],
        bold_keywords: list[str],
    ) -> None:
        name, headline, title, bullet, location = texts
        cv = {
            "name": name,
            "headline": headline,
            "location": location,
            "sections": {
                title: [
                    {"name": name, "location": location, "highlights": [bullet]},
                    {"company": title, "position": headline, "date": bullet},
                    {"label": title, "details": bullet},
                    bullet,
                ],
            },
        }
        model = build_rendercv_model_from_commented_map(
            {
                "cv": cv,
                "settings": {
                    "current_date": datetime.date(2025, 6, 1),
                    "bold_keywords": bold_keywords,
                },
            },
            entry_types=standard_entry_types,
        )
        data = build_document_data(
            model, standard_entry_types, connection_order=list(cv)
        )
        project = TypstProject(root=tmp_path_factory.getbasetemp())

        pdf = compile_typst(project, document_body, data, "pdf")

        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")


class TestQueryTypst:
    def test_returns_the_metadata_value(self, tmp_path: pathlib.Path) -> None:
        value = query_typst(
            TypstProject(root=tmp_path),
            '#metadata((a: 1, b: (true, none, "x"))) <value>',
            "value",
        )

        assert value == {"a": 1, "b": [True, None, "x"]}

    def test_passes_the_data(self, tmp_path: pathlib.Path) -> None:
        value = query_typst(
            TypstProject(root=tmp_path),
            "#metadata(data.numbers.sum()) <value>",
            "value",
            {"numbers": [1, 2, 3]},
        )

        assert value == 6

    def test_raises_user_errors(self, tmp_path: pathlib.Path) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"^Typst couldn't compile the CV: boom$",
        ):
            query_typst(TypstProject(root=tmp_path), '#panic("boom")', "value")

    def test_raises_if_the_label_is_missing(self, tmp_path: pathlib.Path) -> None:
        with pytest.raises(
            RenderCVUserError, match="expected exactly one element, found 0"
        ):
            query_typst(TypstProject(root=tmp_path), "Nothing", "value")


class TestReadEntryTypeDeclarations:
    def test_reads_the_standard_entry_types(self, tmp_path: pathlib.Path) -> None:
        declarations = read_entry_type_declarations(TypstProject(root=tmp_path))

        assert sorted(declarations) == sorted(standard_entry_type_names)
        assert list(declarations["experience"]["fields"]) == [
            "company",
            "position",
            "date",
            "start_date",
            "end_date",
            "location",
            "summary",
            "highlights",
        ]
        assert declarations["experience"]["fields"]["company"] == {
            "kind": "markdown",
            "optional": False,
            "doc": "The company or organization.",
            "of": None,
            "choices": None,
            "pattern": None,
            "allow-text": False,
        }

    def test_reads_a_custom_entries_file(self, tmp_path: pathlib.Path) -> None:
        entries_file = tmp_path / "entries.typ"
        entries_file.write_text(
            f'#import "@preview/rendercv:{version}": entry-type, field, as-entry,'
            " normal\n"
            "#let talk = entry-type(\n"
            '  doc: "A talk.",\n'
            "  fields: (\n"
            '    title: field("markdown"),\n'
            '    level: field("choice", choices: ("invited", "contributed")),\n'
            '    tags: field("list", of: "text", optional: true),\n'
            '    date: field("date", allow-text: true, doc: "When."),\n'
            '    code: field("text", pattern: "[A-Z]+", optional: true),\n'
            "  ),\n"
            '  look: (it, ctx) => as-entry("normal", name: it.title),\n'
            ")\n"
            "#let not-an-entry-type = 42\n",
            encoding="utf-8",
        )
        project = TypstProject(root=tmp_path, entries_file_path=entries_file)

        declarations = read_entry_type_declarations(project)

        assert sorted(declarations) == ["normal", "talk"]
        assert declarations["talk"] == {
            "doc": "A talk.",
            "fields": {
                "title": {
                    "kind": "markdown",
                    "optional": False,
                    "doc": None,
                    "of": None,
                    "choices": None,
                    "pattern": None,
                    "allow-text": False,
                },
                "level": {
                    "kind": "choice",
                    "optional": False,
                    "doc": None,
                    "of": None,
                    "choices": ["invited", "contributed"],
                    "pattern": None,
                    "allow-text": False,
                },
                "tags": {
                    "kind": "list",
                    "optional": True,
                    "doc": None,
                    "of": "text",
                    "choices": None,
                    "pattern": None,
                    "allow-text": False,
                },
                "date": {
                    "kind": "date",
                    "optional": False,
                    "doc": "When.",
                    "of": None,
                    "choices": None,
                    "pattern": None,
                    "allow-text": True,
                },
                "code": {
                    "kind": "text",
                    "optional": True,
                    "doc": None,
                    "of": None,
                    "choices": None,
                    "pattern": "[A-Z]+",
                    "allow-text": False,
                },
            },
        }

    def test_reports_errors_in_the_entries_file(self, tmp_path: pathlib.Path) -> None:
        entries_file = tmp_path / "entries.typ"
        entries_file.write_text("#let talk = (\n", encoding="utf-8")
        project = TypstProject(root=tmp_path, entries_file_path=entries_file)

        with pytest.raises(
            RenderCVUserError,
            match=(
                r"^Typst couldn't compile the CV: unclosed delimiter\n\n"
                r"In `entries\.typ`, line 1, column 12\.$"
            ),
        ):
            read_entry_type_declarations(project)

    def test_uses_the_declarations_body(self, tmp_path: pathlib.Path) -> None:
        assert query_typst(
            TypstProject(root=tmp_path), declarations_body, "rendercv-declarations"
        ) == read_entry_type_declarations(TypstProject(root=tmp_path))


class TestRenderMarkdown:
    def test_renders_markdown(self, sample_project: Project) -> None:
        markdown = render_markdown(
            sample_project.typst_project, sample_project.data, plain=False
        )

        assert markdown.startswith("# John Doe\n\n")
        assert "\n## Experience\n" in markdown
        assert "\n### Nexus AI, Co-Founder & CTO\n" in markdown
        assert "[FlashInfer](https://github.com/)" in markdown
        assert markdown.endswith("\n")

    def test_renders_plain_text(self, sample_project: Project) -> None:
        text = render_markdown(
            sample_project.typst_project, sample_project.data, plain=True
        )

        assert text.startswith("John Doe\n\n")
        assert "\nExperience\n" in text
        assert "#" not in text.split("\n", 1)[0]
        assert "**" not in text
        assert "](" not in text


class TestFindUserFileLocation:
    def test_skips_packages_and_the_main_file(self) -> None:
        diagnostic = (
            "error: panicked with: Unknown design option\n"
            "   ┌─ @preview/rendercv:3.0.0/src/options.typ:41:6\n"
            "   │\n"
            "help: while calling `classic`\n"
            "  ┌─ ../../tmp/cv/design.typ:3:14\n"
            "  │\n"
            "help: while importing `/design.typ`\n"
            "  ┌─ ../../tmp/cv/__typst_py_bytes__.typ:4:1\n"
        )

        assert find_user_file_location(diagnostic) == (
            "`../../tmp/cv/design.typ`, line 3, column 14"
        )

    def test_writes_paths_relative_to_the_root(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / "cv").mkdir()
        monkeypatch.chdir(tmp_path)
        diagnostic = "error: boom\n  ┌─ cv/design.typ:3:14\n"

        assert find_user_file_location(diagnostic, tmp_path / "cv") == (
            "`design.typ`, line 3, column 14"
        )
        assert find_user_file_location(diagnostic, tmp_path / "other") == (
            "`cv/design.typ`, line 3, column 14"
        )

    def test_returns_none_without_a_user_file(self) -> None:
        diagnostic = (
            "error: boom\n"
            "  ┌─ __typst_py_bytes__.typ:6:1\n"
            "   ┌─ @preview/rendercv:3.0.0/lib.typ:1:1\n"
        )

        assert find_user_file_location(diagnostic) is None

    def test_points_at_the_design_file(self, tmp_path: pathlib.Path) -> None:
        design_file = tmp_path / "design.typ"
        design_file.write_text(
            f'#import "@preview/rendercv:{version}": designs\n'
            "#let design = designs.classic(\n"
            '  page: (sise: "a4"),\n'
            ")\n",
            encoding="utf-8",
        )
        project = TypstProject(root=tmp_path, design_file_path=design_file)

        with pytest.raises(
            RenderCVUserError,
            match=(
                r"Did you mean `size`\?.*\n\n"
                r"In `design\.typ`, line 2, column 14\.$"
            ),
        ):
            compile_typst(project, document_body, {}, "pdf")
