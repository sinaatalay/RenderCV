import copy
import re
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError
from rendercv.renderer.typst_compiler import TypstProject, compile_typst

type TypstValue = Callable[..., Any]
type RenderedWords = Callable[..., list[tuple[str, str]]]

design_names = [
    "classic",
    "moderncv",
    "sb2nov",
    "engineeringresumes",
    "engineeringclassic",
    "harvard",
    "ink",
    "ember",
    "opal",
]

talk_type = """#let talk = rendercv.entry-type(
  fields: (title: rendercv.field("markdown"), event: rendercv.field("markdown"), date: rendercv.field("date")),
  look: (it, ctx) => rendercv.as-entry("normal", name: [#it.title at #it.event], date: it.date, location: it.event),
)"""


def media_boxes(pdf: bytes) -> set[str]:
    return {
        box.decode() for box in re.findall(rb"/MediaBox\s*\[\s*([^\]]*?)\s*\]", pdf)
    }


def test_names(typst_value: TypstValue) -> None:
    names = typst_value("rendercv.designs.names")

    assert names == design_names
    assert typst_value(
        "rendercv.designs.names.all(name => type(dictionary(rendercv.designs)"
        ".at(name)) == function)"
    )


@pytest.mark.parametrize("name", design_names)
class TestBuiltInDesigns:
    def test_renders_the_sample_cv(
        self,
        package_project: TypstProject,
        sample_data: dict[str, Any],
        name: str,
    ) -> None:
        pdf = compile_typst(
            package_project,
            f"#rendercv.render(data, types: all-types, design: rendercv.designs.{name}())",
            sample_data,
            "pdf",
        )

        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")

    def test_is_a_complete_design(self, typst_value: TypstValue, name: str) -> None:
        design = typst_value(
            f"rendercv.designs.{name}().pairs().map(((key, value)) => (key,"
            ' if type(value) == function { "function" } else if key == "entries"'
            ' { value.keys() } else if key in ("options", "parts") { value.keys() }'
            " else { value })).to-dict()"
        )

        assert design == {
            "name": name,
            "options": [
                "page",
                "colors",
                "typography",
                "links",
                "header",
                "section_titles",
                "sections",
                "entries",
                "templates",
            ],
            "document": "function",
            "header": "function",
            "section": "function",
            "entries": [
                "normal",
                "experience",
                "education",
                "publication",
                "one_line",
                "bullet",
                "numbered",
                "reversed_numbered",
                "paragraph",
            ],
            "parts": [
                "regular-entry",
                "text-entry",
                "entry-dates",
                "entry-body",
                "summary-block",
                "lines",
                "degree-with-area",
                "publication-link",
                "dash-location",
            ],
        }

    def test_takes_options(self, typst_value: TypstValue, name: str) -> None:
        options = typst_value(
            f'rendercv.designs.{name}(page: (size: "a4"), colors: (name: red),'
            ' typography: (font_family: "Libertinus Serif")).options'
        )

        assert options["page"]["size"] == "a4"
        assert options["colors"]["name"] == 'rgb("#ff4136")'
        assert set(options["typography"]["font_family"].values()) == {
            "Libertinus Serif"
        }

    def test_exposes_the_parts_of_its_looks(
        self, typst_value: TypstValue, name: str
    ) -> None:
        parts = typst_value(f"rendercv.designs.{name}().parts.keys()")

        assert {"regular-entry", "text-entry", "entry-dates", "entry-body"} <= set(
            parts
        )

    def test_explains_typos_in_options(
        self, typst_value: TypstValue, name: str
    ) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=(
                r"Unknown design option `page\.sise`\. Did you mean `size`\?"
                r" Available options here: `size`, `top_margin`"
            ),
        ):
            typst_value(f'rendercv.designs.{name}(page: (sise: "a4"))')

    def test_explains_wrong_option_types(
        self, typst_value: TypstValue, name: str
    ) -> None:
        with pytest.raises(
            RenderCVUserError,
            match=r"Design option `colors\.name` should be of type color",
        ):
            typst_value(f'rendercv.designs.{name}(colors: (name: "blue"))')

    def test_lets_entry_types_be_restyled(
        self,
        rendered_words: RenderedWords,
        sample_data: dict[str, Any],
        name: str,
    ) -> None:
        words = rendered_words(
            sample_data,
            design="restyled",
            prelude=(
                f"#let restyled = rendercv.designs.{name}()\n"
                "#let restyled = restyled + (entries: restyled.entries + (experience:"
                " (it, ctx) => [RESTYLED #it.company]))"
            ),
        )
        text = " ".join(word for word, weight in words)

        assert "RESTYLED Nexus AI" in text
        assert "RESTYLED NVIDIA Research" in text
        assert "Co-Founder" not in text

    def test_styles_custom_entry_types_that_hand_over_to_normal(
        self,
        rendered_words: RenderedWords,
        sample_data: dict[str, Any],
        name: str,
    ) -> None:
        talk_data = copy.deepcopy(sample_data)
        talk_data["sections"] = [
            {
                "key": "talks",
                "title": ["Talks"],
                "entries": [
                    {
                        "type": "talk",
                        "fields": {
                            "title": ["Typst for CVs"],
                            "event": ["TypstConf"],
                            "date": {"year": 2024, "month": 5},
                        },
                    }
                ],
            }
        ]
        normal_data = copy.deepcopy(talk_data)
        normal_data["sections"][0]["entries"] = [
            {
                "type": "normal",
                "fields": {
                    "name": ["Typst for CVs at TypstConf"],
                    "date": {"year": 2024, "month": 5},
                    "location": ["TypstConf"],
                },
            }
        ]
        design = f"rendercv.designs.{name}()"

        talk_words = rendered_words(
            talk_data,
            design=design,
            types="all-types + (talk: talk)",
            prelude=talk_type,
        )

        assert talk_words == rendered_words(normal_data, design=design)
        assert ("Typst", "regular") in talk_words or ("Typst", "bold") in talk_words


class TestPageOptions:
    def test_uses_us_letter_by_default(
        self, package_project: TypstProject, sample_data: dict[str, Any]
    ) -> None:
        pdf = compile_typst(
            package_project,
            "#rendercv.render(data, types: all-types, design: rendercv.designs.classic())",
            sample_data,
            "pdf",
        )

        assert isinstance(pdf, bytes)
        assert media_boxes(pdf) == {"0 0 612 792"}

    def test_uses_the_chosen_page_size(
        self, package_project: TypstProject, sample_data: dict[str, Any]
    ) -> None:
        pdf = compile_typst(
            package_project,
            "#rendercv.render(data, types: all-types, design:"
            ' rendercv.designs.classic(page: (size: "a4")))',
            sample_data,
            "pdf",
        )

        assert isinstance(pdf, bytes)
        assert media_boxes(pdf) == {"0 0 595.2756 841.8898"}


def test_designs_can_be_extended_with_their_parts(
    rendered_words: RenderedWords, sample_data: dict[str, Any]
) -> None:
    words = rendered_words(
        sample_data,
        design=(
            "rendercv.designs.classic() + (section: (section, body, ctx) =>"
            " [SECTION #section.title #body])"
        ),
    )
    text = " ".join(word for word, weight in words)

    assert "SECTION Education" in text
    assert "SECTION Experience" in text
