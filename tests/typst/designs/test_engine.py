import copy
import pathlib
import shutil
from collections.abc import Callable
from typing import Any

import pytest

from rendercv.exception import RenderCVUserError
from rendercv.renderer.typst_compiler import TypstProject, compile_typst, document_body
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.models.locale.locale import Locale

type TypstValue = Callable[..., Any]
type RenderedWords = Callable[..., list[tuple[str, str]]]
type CvData = Callable[..., dict[str, Any]]

prelude = '#import "/designs/engine.typ": engine, resolve-options, defaults'

profile_picture = (
    pathlib.Path(__file__).parents[2] / "renderer" / "testdata" / "profile_picture.jpg"
)


experience: dict[str, Any] = {
    "company": "Acme",
    "position": "Engineer",
    "start_date": "2023-06",
    "end_date": "present",
}


def text_of(words: list[tuple[str, str]]) -> str:
    return " ".join(word for word, weight in words)


def render_text(
    rendered_words: RenderedWords, data: dict[str, Any], options: str = ""
) -> str:
    return text_of(rendered_words(data, design=f"rendercv.designs.classic({options})"))


def test_defaults(typst_value: TypstValue) -> None:
    assert typst_value("defaults.keys()", prelude=prelude) == [
        "page",
        "colors",
        "typography",
        "links",
        "header",
        "section_titles",
        "sections",
        "entries",
        "templates",
    ]


class TestResolveOptions:
    def test_merges_design_defaults_then_user_values(
        self, typst_value: TypstValue
    ) -> None:
        options = typst_value(
            'resolve-options((page: (size: "a4", top_margin: 1cm)), (page:'
            " (top_margin: 2cm))).page",
            prelude=prelude,
        )

        assert options["size"] == "a4"
        assert options["top_margin"] == "56.69pt"
        assert options["bottom_margin"] == "50.4pt"

    def test_accepts_one_font_for_everything(self, typst_value: TypstValue) -> None:
        assert typst_value(
            'resolve-options((typography: (font_family: "Fontin")), (:))'
            ".typography.font_family",
            prelude=prelude,
        ) == dict.fromkeys(
            ["body", "name", "headline", "connections", "section_titles"], "Fontin"
        )
        assert typst_value(
            'resolve-options((:), (typography: (font_family: "Fontin")))'
            ".typography.font_family.name",
            prelude=prelude,
        ) == ("Fontin")

    def test_accepts_fonts_per_element(self, typst_value: TypstValue) -> None:
        fonts = typst_value(
            'resolve-options((:), (typography: (font_family: (name: "Fontin"))))'
            ".typography.font_family",
            prelude=prelude,
        )

        assert fonts["name"] == "Fontin"
        assert fonts["body"] == "Source Sans 3"

    def test_rejects_unknown_options(self, typst_value: TypstValue) -> None:
        with pytest.raises(
            RenderCVUserError, match=r"Unknown design option `header\.photo_size`"
        ):
            typst_value(
                "resolve-options((:), (header: (photo_size: 1cm)))", prelude=prelude
            )


class TestEngine:
    def test_builds_a_design(self, typst_value: TypstValue) -> None:
        design = typst_value(
            'engine(resolve-options((:), (:)), name: "mine")', prelude=prelude
        )

        assert design["name"] == "mine"
        assert list(design["entries"]) == [
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

    def test_lets_designs_add_entry_looks_from_the_parts(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data(
            {"sections": {"skills": [{"label": "Languages", "details": "Python"}]}}
        )

        words = rendered_words(
            data,
            design="mine",
            prelude=(
                prelude + "\n#let mine = engine(resolve-options((:), (:)), entries:"
                " (o, parts) => (one_line: (it, ctx) => (parts.text-entry)(ctx,"
                " [#it.details (#it.label)])))"
            ),
        )

        assert "Python (Languages)" in text_of(words)


class TestHeader:
    @pytest.mark.parametrize(
        ("options", "expected", "unexpected"),
        [
            ("", ["", "jane@doe.com", "(609) 555-0100", "janedoe"], []),
            (
                "header: (connections: (show_icons: false))",
                ["jane@doe.com"],
                [""],
            ),
            (
                'header: (connections: (phone_number_format: "international"))',
                ["+1 609-555-0100"],
                ["(609) 555-0100"],
            ),
            (
                'header: (connections: (phone_number_format: "e164"))',
                ["+16095550100"],
                [],
            ),
            (
                "header: (connections: (display_urls_instead_of_usernames: true))",
                ["github.com/janedoe", "(609) 555-0100"],
                [],
            ),
            (
                'header: (connections: (separator: "~", show_icons: false))',
                ["Istanbul ~ jane@doe.com ~"],
                [],
            ),
        ],
    )
    def test_draws_connections(
        self,
        rendered_words: RenderedWords,
        cv_data: CvData,
        options: str,
        expected: list[str],
        unexpected: list[str],
    ) -> None:
        data = cv_data(
            {
                "name": "Jane Doe",
                "location": "Istanbul",
                "email": "jane@doe.com",
                "phone": "+1 609 555 0100",
                "social_networks": [{"network": "GitHub", "username": "janedoe"}],
            }
        )

        text = render_text(rendered_words, data, options)

        for part in expected:
            assert part in text
        for part in unexpected:
            assert part not in text

    @pytest.mark.parametrize("position", ["left", "right"])
    def test_draws_a_photo(
        self, tmp_path: pathlib.Path, cv_data: CvData, position: str
    ) -> None:
        shutil.copy(profile_picture, tmp_path / "photo.jpg")
        data = cv_data({"name": "Jane Doe", "headline": "Engineer"})
        data["header"]["photo"] = "/photo.jpg"
        design_file = tmp_path / "design.typ"
        design_file.write_text(
            f'#import "@preview/rendercv:{get_rendercv_typst_version()}": designs\n'
            f'#let design = designs.classic(header: (photo_position: "{position}"))\n',
            encoding="utf-8",
        )

        pdf = compile_typst(
            TypstProject(root=tmp_path, design_file_path=design_file),
            document_body,
            data,
            "pdf",
        )

        assert isinstance(pdf, bytes)
        assert b"/Subtype/Image" in pdf

    def test_draws_the_headline(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data({"name": "Jane Doe", "headline": "Research *Engineer*"})

        text = render_text(
            rendered_words,
            data,
            "typography: (small_caps: (name: true, headline: true, connections:"
            " true, section_titles: true), bold: (headline: true))",
        )

        assert "Jane Doe Research Engineer" in text


class TestPage:
    def test_shows_the_top_note_and_footer(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        text = render_text(rendered_words, cv_data({"name": "Jane Doe"}))

        assert text.startswith("Last updated in June 2025")
        assert text.endswith("Jane Doe – 1/1")

    def test_hides_the_top_note_and_footer(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        text = render_text(
            rendered_words,
            cv_data({"name": "Jane Doe"}),
            "page: (show_top_note: false, show_footer: false)",
        )

        assert text == "Jane Doe"

    def test_uses_custom_templates(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        text = render_text(
            rendered_words,
            cv_data(
                {
                    "name": "Jane Doe",
                    "sections": {
                        "experience": [
                            {
                                "company": "Acme",
                                "position": "Engineer",
                                "start_date": "2020-01",
                                "end_date": "2021-03",
                            }
                        ]
                    },
                }
            ),
            "templates: (footer: info => [Footer of #info.name], top_note: info =>"
            " [Updated #(info.format-date)(info.current-date)], single_date: (date,"
            " locale) => [#date.month.#date.year], date_range: (start, end) =>"
            " [#start until #end], time_span: (start, end, ctx) => [SPAN])",
        )

        assert text.startswith("Updated 6.2025")
        assert "1.2020 until 3.2021 SPAN" in text
        assert text.endswith("Footer of Jane Doe")


class TestSections:
    def test_shows_time_spans_in_chosen_sections(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "experience": [experience],
                    "projects": [{"name": "Project", "start_date": "2023-06"}],
                }
            }
        )

        text = render_text(rendered_words, data)

        assert "June 2023 – present 2 years 1 month" in text
        assert text.count("years") == 1

    def test_shows_time_spans_in_subsections_of_chosen_sections(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data({"sections": {"experience": {"Industry": [experience]}}})

        assert "2 years 1 month" in render_text(rendered_words, data)

    def test_hides_time_spans(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data({"sections": {"experience": [experience]}})

        text = render_text(rendered_words, data, "sections: (show_time_spans_in: ())")

        assert "years" not in text

    @pytest.mark.parametrize(
        "title_type",
        [
            "with_partial_line",
            "with_full_line",
            "without_line",
            "moderncv",
            "centered_without_line",
            "centered_with_partial_line",
            "centered_with_centered_partial_line",
            "centered_with_full_line",
        ],
    )
    def test_draws_every_section_title_type(
        self,
        rendered_words: RenderedWords,
        sample_data: dict[str, Any],
        title_type: str,
    ) -> None:
        text = render_text(
            rendered_words,
            sample_data,
            f'section_titles: (type: "{title_type}")',
        )

        assert "Education" in text
        assert "Princeton University" in text


class TestEntries:
    @pytest.mark.parametrize(
        "options",
        [
            "entries: (short_second_row: false)",
            "entries: (short_second_row: true)",
            'typography: (alignment: "left")',
            'typography: (alignment: "justified-with-no-hyphenation")',
            "links: (underline: true, show_external_link_icon: true)",
            "entries: (allow_page_break: true), sections: (allow_page_break: false)",
            'section_titles: (type: "moderncv"), entries: (short_second_row: false)',
        ],
    )
    def test_draws_the_sample_cv_with_options(
        self,
        package_project: TypstProject,
        sample_data: dict[str, Any],
        options: str,
    ) -> None:
        pdf = compile_typst(
            package_project,
            "#rendercv.render(data, types: all-types, design:"
            f" rendercv.designs.classic({options}))",
            sample_data,
            "pdf",
        )

        assert isinstance(pdf, bytes)

    def test_draws_the_degree_in_its_own_column(
        self, rendered_words: RenderedWords, cv_data: CvData
    ) -> None:
        data = cv_data(
            {
                "sections": {
                    "education": [
                        {
                            "institution": "MIT",
                            "area": "Physics",
                            "degree": "PhD",
                            "summary": "Thesis",
                            "highlights": ["Advisor"],
                        }
                    ]
                }
            }
        )

        text = render_text(
            rendered_words, data, "page: (show_top_note: false, show_footer: false)"
        )

        # The degree comes first, in its own column:
        assert text == "Education PhD MIT , Physics Thesis • Advisor"

    def test_draws_every_standard_entry_type(
        self, rendered_words: RenderedWords, sample_data: dict[str, Any]
    ) -> None:
        text = render_text(rendered_words, sample_data)

        for part in [
            "Nexus AI , Co-Founder & CTO",
            "PhD Princeton University , Computer Science",
            "FlashInfer",
            "Sparse Mixture-of-Experts at Scale",
            "10.1234/neurips.2023.1234 (NeurIPS 2023)",
            "Languages: Python, C++",
            "• MIT Technology Review",
            "1. Adaptive Quantization",
            "4. Scaling Laws",
            "Markdown syntax is supported everywhere.",
        ]:
            assert part in text

    def test_draws_right_to_left_cvs(
        self, rendered_words: RenderedWords, sample_data: dict[str, Any]
    ) -> None:
        data = copy.deepcopy(sample_data)
        data["locale"] = Locale.model_validate({"language": "arabic"}).model_dump()

        text = render_text(rendered_words, data)

        assert data["locale"]["direction"] == "rtl"
        assert data["locale"]["present"] in text
        assert "Princeton University" in text
