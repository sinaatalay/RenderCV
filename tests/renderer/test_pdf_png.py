import contextlib
import io
import json
import pathlib
import re
import zlib
from unittest.mock import MagicMock, patch

import pytest
import rendercv_fonts
import typst

import rendercv.renderer
from rendercv.exception import RenderCVInternalError
from rendercv.renderer.pdf_png import (
    generate_pdf,
    generate_png,
    generate_svg,
    get_package_path,
    read_version_from_typst_toml,
    write_pages,
)
from rendercv.renderer.templater.templater import render_full_template
from rendercv.renderer.typst import generate_typst, render_typst_source
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model


@pytest.mark.usefixtures("bundled_fonts_only")
@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_pdf(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        model.settings.render_command.pdf_path = output_path
        generate_pdf(model)

    reference_filename = f"{theme}_{cv_variant}.pdf"

    assert compare_file_with_reference(generate_file, reference_filename)


@pytest.mark.usefixtures("bundled_fonts_only")
@pytest.mark.parametrize("theme", available_themes)
def test_generate_png(
    compare_file_with_reference,
    theme: str,
    minimal_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": theme},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        model.settings.render_command.png_path = output_path
        generate_png(model)

    reference_filename = f"{theme}_minimal.png"

    assert compare_file_with_reference(generate_file, reference_filename)


class TestGetPackagePath:
    def test_creates_correct_directory_structure(self):
        get_package_path.cache_clear()
        result = get_package_path()

        # Find the version-named directory under preview/rendercv/:
        rendercv_package_dir = result / "preview" / "rendercv"
        assert rendercv_package_dir.is_dir()

        version_dirs = list(rendercv_package_dir.iterdir())
        assert len(version_dirs) == 1

        package_dir = version_dirs[0]
        assert (package_dir / "typst.toml").is_file()
        assert (package_dir / "lib.typ").is_file()

    def test_returns_cached_result(self):
        get_package_path.cache_clear()
        first_result = get_package_path()
        second_result = get_package_path()
        assert first_result == second_result

    def test_raises_error_when_version_missing_from_typst_toml(self, tmp_path):
        get_package_path.cache_clear()
        toml_file = tmp_path / "typst.toml"
        toml_file.write_text('[package]\nname = "rendercv"\n', encoding="utf-8")
        with pytest.raises(
            RenderCVInternalError,
            match=r"Could not find version in",
        ):
            read_version_from_typst_toml(toml_file)


class TestWritePages:
    def test_writes_numbered_files_and_replaces_the_previous_pages(self, tmp_path):
        for number in (1, 2, 3):
            (tmp_path / f"cv_{number}.png").write_bytes(b"old")

        result = write_pages([b"a", b"b"], tmp_path / "cv.png")

        assert result == [tmp_path / "cv_1.png", tmp_path / "cv_2.png"]
        assert sorted(path.name for path in tmp_path.iterdir()) == [
            "cv_1.png",
            "cv_2.png",
        ]
        assert (tmp_path / "cv_2.png").read_bytes() == b"b"

    def test_leaves_other_files_alone(self, tmp_path):
        others = ["cv_backup.png", "other_1.png", "cv_1.svg", "cv.png"]
        for name in others:
            (tmp_path / name).write_bytes(b"other")

        write_pages([b"a"], tmp_path / "cv.png")

        assert all((tmp_path / name).read_bytes() == b"other" for name in others)


def test_raises_error_when_typst_returns_none_bytes(
    tmp_path: pathlib.Path,
    minimal_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": "classic"},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    model.settings.render_command.typst_path = output_dir / "John_Doe_CV.typ"
    model.settings.render_command.png_path = output_dir / "John_Doe_CV.png"

    mock_compiler = MagicMock()
    mock_compiler.compile.return_value = [None]

    with (
        patch(
            "rendercv.renderer.pdf_png.get_typst_compiler", return_value=mock_compiler
        ),
        pytest.raises(RenderCVInternalError, match="Typst returned no PNG output"),
    ):
        generate_png(model)


@pytest.mark.parametrize("pdf", [False, True])
@pytest.mark.parametrize("png", [False, True])
def test_compiles_without_writing_typst(tmp_path, minimal_rendercv_model, pdf, png):
    model = minimal_rendercv_model
    command = model.settings.render_command
    command.dont_generate_typst = True
    command.dont_generate_pdf = not pdf
    command.dont_generate_png = not png
    command.typst_path = tmp_path / "cv.typ"
    command.pdf_path = tmp_path / "cv.pdf"
    command.png_path = tmp_path / "cv.png"
    assert generate_typst(model) is None
    assert (generate_pdf(model) is not None) == pdf
    assert (generate_png(model) is not None) == png
    assert not list(tmp_path.rglob("*.typ"))


@pytest.mark.parametrize(
    "generate", [generate_typst, generate_pdf, generate_png, generate_svg]
)
def test_photo_is_next_to_the_typst_file(tmp_path, minimal_rendercv_model, generate):
    model = minimal_rendercv_model
    photo = pathlib.Path(__file__).parent / "testdata" / "profile_picture.jpg"
    model.cv.photo = photo
    command = model.settings.render_command
    command.typst_path = tmp_path / "output" / "cv.typ"
    command.pdf_path = tmp_path / "output" / "cv.pdf"
    command.png_path = tmp_path / "output" / "cv.png"
    command.svg_path = tmp_path / "output" / "cv.svg"

    assert 'image("profile_picture.jpg"' in render_typst_source(model)
    assert generate(model) is not None
    assert (tmp_path / "output" / photo.name).read_bytes() == photo.read_bytes()


def test_photo_already_next_to_the_typst_file_is_kept(tmp_path, minimal_rendercv_model):
    photo = tmp_path / "profile_picture.jpg"
    photo.write_bytes(
        (pathlib.Path(__file__).parent / "testdata" / photo.name).read_bytes()
    )
    model = minimal_rendercv_model
    model.cv.photo = photo
    model.settings.render_command.typst_path = tmp_path / "cv.typ"

    # Copying a file onto itself would raise `shutil.SameFileError`:
    assert generate_typst(model) is not None
    assert photo.exists()


@pytest.mark.parametrize(
    "url", ["https://example.com/photo.jpg", "https://example.com/"]
)
def test_validated_remote_photo_renders_without_another_download(tmp_path, url):
    photo = pathlib.Path(__file__).parent / "testdata/profile_picture.jpg"
    with patch(
        "rendercv.schema.models.path.urllib.request.urlopen",
        return_value=io.BytesIO(photo.read_bytes()),
    ):
        model = RenderCVModel.model_validate(
            {"cv": {"name": "Jane Doe", "photo": url}},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
            },
        )
    with patch(
        "rendercv.schema.models.path.urllib.request.urlopen",
        side_effect=AssertionError("rendering must not fetch inputs"),
    ):
        pdf = generate_pdf(model)
    assert pdf is not None
    assert pdf.read_bytes().startswith(b"%PDF")


def test_saved_typst_file_compiles_on_its_own(tmp_path, minimal_rendercv_model):
    model = minimal_rendercv_model
    model.cv.photo = pathlib.Path(__file__).parent / "testdata" / "profile_picture.jpg"
    model.settings.render_command.typst_path = tmp_path / "cv.typ"
    typst_path = generate_typst(model)
    assert typst_path is not None

    pdf = typst.compile(typst_path, package_path=get_package_path())

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")


def test_png_failure_preserves_previous_output(tmp_path, minimal_rendercv_model):

    model = minimal_rendercv_model
    model.settings.render_command.png_path = tmp_path / "cv.png"
    previous = tmp_path / "cv_1.png"
    previous.write_bytes(b"previous output")
    compiler = MagicMock()
    compiler.compile.side_effect = typst.TypstError("invalid", "invalid")
    with (
        patch("rendercv.renderer.pdf_png.get_typst_compiler", return_value=compiler),
        pytest.raises(typst.TypstError),
    ):
        generate_png(model, "invalid")
    assert previous.read_bytes() == b"previous output"


def test_generate_svg(tmp_path, minimal_rendercv_model):
    model = minimal_rendercv_model
    model.settings.render_command.svg_path = tmp_path / "cv.svg"

    result = generate_svg(model)

    assert result == [tmp_path / "cv_1.svg"]
    assert (tmp_path / "cv_1.svg").read_bytes().startswith(b"<svg")


def test_generate_svg_can_be_disabled(tmp_path, minimal_rendercv_model):
    model = minimal_rendercv_model
    model.settings.render_command.svg_path = tmp_path / "cv.svg"
    model.settings.render_command.dont_generate_svg = True

    assert generate_svg(model) is None
    assert not list(tmp_path.iterdir())


class TestPdfStandards:
    def test_pdf_conforms_to_pdf_ua_1_by_default(self, tmp_path, full_rendercv_model):
        model = full_rendercv_model
        model.settings.render_command.typst_path = tmp_path / "cv.typ"
        model.settings.render_command.pdf_path = tmp_path / "cv.pdf"

        pdf = generate_pdf(model)

        assert pdf is not None
        assert b"pdfuaid" in zlib_streams(pdf.read_bytes())

    def test_compiler_errors_propagate(self, tmp_path, minimal_rendercv_model):
        model = minimal_rendercv_model
        model.settings.render_command.typst_path = tmp_path / "cv.typ"
        model.settings.render_command.pdf_path = tmp_path / "cv.pdf"
        photo = pathlib.Path(__file__).parent / "testdata" / "profile_picture.jpg"
        (tmp_path / "photo.jpg").write_bytes(photo.read_bytes())
        source = render_typst_source(model) + '\n#image("photo.jpg")\n'

        with pytest.raises(typst.TypstError, match="PDF/UA-1"):
            generate_pdf(model, source)


def zlib_streams(pdf: bytes) -> bytes:
    """Decompress the compressed streams of a PDF, where its XMP metadata is."""
    decompressed = []
    for stream in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf, re.DOTALL):
        with contextlib.suppress(zlib.error):
            decompressed.append(zlib.decompress(stream))
    return b"\n".join([pdf, *decompressed])


@pytest.mark.parametrize("filler_lines", range(30, 45))
def test_entry_header_never_ends_a_page_alone(tmp_path, filler_lines):
    # Raw Typst in the content records the pages of the header and the first
    # highlight, which some of these filler lengths would separate:
    def page_of(label: str) -> str:
        return f"#box[#context [#metadata(here().page())<{label}>]]"

    filler = "\n".join(
        f"      - Filler line {line} with enough words to fill a line."
        for line in range(filler_lines)
    )
    yaml = f"""cv:
  name: Jane Doe
  sections:
    filler:
{filler}
    experience:
      - company: "Acme {page_of("header")}"
        position: Engineer
        highlights:
          - "{page_of("highlight")}First highlight"
          - Second highlight
design:
  theme: classic
  entries:
    allow_page_break: true
"""
    _, model = build_rendercv_dictionary_and_model(
        yaml, input_file_path=tmp_path / "cv.yaml"
    )
    source = render_typst_source(model).encode()

    pages = [
        typst.query(
            source,
            f"<{label}>",
            field="value",
            one=True,
            package_path=get_package_path(),
            font_paths=typst.Fonts(font_paths=rendercv_fonts.paths_to_font_folders),
        )
        for label in ("header", "highlight")
    ]

    assert pages[0] == pages[1]


@pytest.mark.parametrize("theme", available_themes)
def test_recursive_subsections_compile_with_every_theme(tmp_path, theme):
    entries = [{"company": "Acme", "position": "Engineer", "highlights": ["**Work**"]}]
    for depth in range(8):
        entries = [{"title": f"Group {depth}", "entries": entries}]
    _, model = build_rendercv_dictionary_and_model(
        json.dumps(
            {
                "cv": {"name": "Jane Doe", "sections": {"work": entries}},
                "design": {"theme": theme},
            }
        ),
        input_file_path=tmp_path / "cv.yaml",
    )
    model.settings.render_command.pdf_path = tmp_path / "cv.pdf"
    pdf = generate_pdf(model)
    assert pdf is not None
    assert pdf.read_bytes().startswith(b"%PDF")
    markdown = render_full_template(model, "markdown")
    assert "## Work" in markdown
    assert "### Group 7" in markdown
    assert 'aria-level="10"' in markdown
    assert 'aria-level="11"' in markdown
    assert "Acme" in markdown


def test_subsection_titles_have_space_above_only_below_content(tmp_path):
    # Raw Typst in the titles records their vertical positions in points:
    def position_of(label: str) -> str:
        return f"#box[#context [#metadata(here().position().y / 1pt)<{label}>]]"

    def positions(space_above: str) -> list[float]:
        yaml = f"""cv:
  name: Jane Doe
  sections:
    publications:
      - title: "{position_of("first")}Journal Articles"
        entries:
          - A paper.
      - title: "{position_of("second")}Talks"
        entries:
          - A talk.
design:
  theme: classic
  subsection_titles:
    space_above: {space_above}
"""
        _, model = build_rendercv_dictionary_and_model(
            yaml, input_file_path=tmp_path / "cv.yaml"
        )
        source = render_typst_source(model).encode()
        return [
            float(
                typst.query(
                    source,
                    f"<{label}>",
                    field="value",
                    one=True,
                    package_path=get_package_path(),
                    font_paths=typst.Fonts(
                        font_paths=rendercv_fonts.paths_to_font_folders
                    ),
                )
            )
            for label in ("first", "second")
        ]

    first, second = positions("0.5cm")
    first_with_more_space, second_with_more_space = positions("1.5cm")

    # The first subsection title is below its section's title, not below content:
    assert first_with_more_space == pytest.approx(first)
    assert second_with_more_space - second == pytest.approx(1 / 2.54 * 72)


@pytest.mark.parametrize(
    ("language", "text", "font"),
    [
        ("mandarin_chinese", "软件工程师，负责后端开发。", b"NotoSansSC"),
        ("japanese", "ソフトウェアー・角", b"NotoSansJP"),
        ("korean", "소프트웨어 엔지니어", b"NotoSansKR"),
    ],
)
def test_renders_chinese_japanese_and_korean_with_the_bundled_fonts(
    tmp_path, language, text, font
):
    yaml = f"cv:\n  name: Jane Doe\n  sections:\n    summary:\n      - {text}\n"
    yaml += f"locale:\n  language: {language}\n"
    _, model = build_rendercv_dictionary_and_model(
        yaml, input_file_path=tmp_path / "cv.yaml"
    )
    model.settings.render_command.pdf_path = tmp_path / "cv.pdf"

    # PDF/UA-1 also makes compilation fail on any character that no font has:
    pdf = generate_pdf(model)

    assert pdf is not None
    assert font in zlib_streams(pdf.read_bytes())


def test_typst_source_imports_the_bundled_rendercv_package(minimal_rendercv_model):
    # Otherwise, Typst would download another version from Typst Universe:
    renderer = pathlib.Path(rendercv.renderer.__file__).parent
    rendercv_version = read_version_from_typst_toml(
        renderer / "rendercv_typst" / "typst.toml"
    )

    source = render_typst_source(minimal_rendercv_model)

    assert f'#import "@preview/rendercv:{rendercv_version}"' in source
