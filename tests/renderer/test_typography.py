import json
import pathlib

import pytest
import rendercv_fonts
import typst

import rendercv.renderer
from rendercv.renderer.pdf_png import (
    get_package_path,
    get_typst_compiler,
    read_version_from_typst_toml,
)
from rendercv.renderer.templater.connections import compute_connections_for_typst
from rendercv.renderer.templater.templater import render_full_template
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("font", ["Lato", "Fontin", "Poppins"])
@pytest.mark.parametrize("word", ["résumé", "éğöç"])
def test_small_caps_synthesizes_accented_letters_when_the_font_lacks_them(font, word):
    manifest = (
        pathlib.Path(rendercv.renderer.__file__).parent / "rendercv_typst/typst.toml"
    )
    version = read_version_from_typst_toml(manifest)
    source = f'''#import "@preview/rendercv:{version}": small-caps
#set text(font: "{font}", size: 12pt)
#context {{
  let bounds(body) = measure(text(top-edge: "bounds", bottom-edge: "bounds", body))
  let actual = bounds(small-caps([{word}]))
  let expected = bounds(text(size: 0.78em, upper([{word}])))
  metadata((actual: (actual.width / 1pt, actual.height / 1pt),
            expected: (expected.width / 1pt, expected.height / 1pt)))
}}'''
    measurements = json.loads(
        typst.query(
            source.encode(),
            "metadata",
            field="value",
            one=True,
            package_path=get_package_path(),
            font_paths=typst.Fonts(font_paths=rendercv_fonts.paths_to_font_folders),
        )
    )
    assert measurements["actual"] == pytest.approx(measurements["expected"])


@pytest.mark.parametrize("phone_format", ["international", "national", "E164"])
def test_arabic_phone_numbers_keep_the_same_visual_order_as_ltr(tmp_path, phone_format):
    model = RenderCVModel.model_validate(
        {
            "cv": {"name": "Jane Doe", "phone": "+14155552671"},
            "locale": {"language": "arabic"},
            "design": {
                "theme": "classic",
                "header": {
                    "connections": {
                        "show_icons": False,
                        "hyperlink": False,
                        "phone_number_format": phone_format,
                    }
                },
            },
        }
    )
    (connection,) = compute_connections_for_typst(model)
    compiler = get_typst_compiler(None, tmp_path)

    def render(direction):
        source = (
            "#set page(width: 250pt, height: 40pt, margin: 0pt)\n"
            f'#set text(font: "Source Sans 3", dir: {direction})\n'
            f"#align(left)[{connection}]"
        )
        return compiler.compile(source.encode(), format="svg")

    assert render("rtl") == render("ltr")


@pytest.mark.parametrize("output_format", ["typst", "markdown"])
def test_sb2nov_uses_the_localized_degree_phrase(output_format):
    model = RenderCVModel.model_validate(
        {
            "cv": {
                "name": "Jane Doe",
                "sections": {
                    "education": [
                        {
                            "institution": "Universidad",
                            "degree": "Licenciatura",
                            "area": "Física",
                        }
                    ]
                },
            },
            "design": {"theme": "sb2nov"},
            "locale": {"language": "spanish"},
        }
    )
    source = render_full_template(model, output_format)
    assert "Licenciatura en Física" in source
    assert " in " not in source


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("output_format", ["typst", "markdown"])
def test_education_degree_appears_once_in_every_theme(theme, output_format):
    model = RenderCVModel.model_validate(
        {
            "cv": {
                "name": "Jane Doe",
                "sections": {
                    "education": [
                        {
                            "institution": "Example University",
                            "degree": "BSc",
                            "area": "Physics",
                        }
                    ]
                },
            },
            "design": {"theme": theme},
        }
    )
    source = render_full_template(model, output_format)
    assert source.count("BSc") == 1
