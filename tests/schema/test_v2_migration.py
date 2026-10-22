import json
import pathlib
from collections.abc import Callable
from typing import Any

import pytest
import typst

from rendercv.renderer.project import Project
from rendercv.renderer.typst_packages import get_rendercv_typst_version
from rendercv.schema.v2_migration import (
    DesignMigration,
    alignment_options,
    convert_color,
    convert_date_template,
    convert_value,
    migrate_design,
    named_colors,
)
from rendercv.schema.yaml_reader import read_yaml

type RenderPdf = Callable[[pathlib.Path], tuple[Project, pathlib.Path]]

v2_designs_directory = pathlib.Path(__file__).parent / "testdata" / "test_v2_migration"
v2_design_files = sorted(v2_designs_directory.glob("*.yaml"))

# A CV that uses dates, so the migrated date templates are used too:
cv_yaml = """cv:
  name: John Doe
  email: john@example.com
  sections:
    experience:
      - company: ACME
        position: Engineer
        start_date: 2020-05
        end_date: 2021-11
        highlights:
          - Built things - with nested bullets
    education:
      - institution: MIT
        area: Computer Science
        degree: BS
        date: 2019-03
settings:
  current_date: 2024-01-01
"""
months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def typst_array(items: list[str]) -> str:
    return "(" + ", ".join(json.dumps(item) for item in items) + ",)"


def evaluate_template(tmp_path: pathlib.Path, function: str, arguments: str) -> str:
    """Call a converted template in Typst and return the text it writes."""
    main = tmp_path / "main.typ"
    main.write_text(
        '#let plain(it) = if type(it) == str { it } else if it.has("text") {'
        ' it.text } else if it.has("children") { it.children.map(plain).sum('
        'default: "") } else if it.func() == [ ].func() { " " } else { "" }\n'
        f"#let locale = (month_names: {typst_array(months)}, month_abbreviations:"
        f" {typst_array([month[:3] for month in months])})\n"
        f"#let template = {function}\n"
        f"#metadata(plain(template({arguments}))) <written>\n",
        encoding="utf-8",
    )
    return json.loads(typst.query(str(main), "<written>", field="value", one=True))


def migrate_and_render(
    tmp_path: pathlib.Path, render_pdf: RenderPdf, design: dict[str, Any]
) -> DesignMigration:
    migration = migrate_design(design, version=get_rendercv_typst_version())
    (tmp_path / "design.typ").write_text(migration.source, encoding="utf-8")
    (tmp_path / "cv.yaml").write_text(cv_yaml, encoding="utf-8")
    project, _ = render_pdf(tmp_path / "cv.yaml")
    assert project.typst_project.design_file_path == tmp_path / "design.typ"
    return migration


class TestConvertColor:
    @pytest.mark.parametrize(
        ("value", "expected_color"),
        [
            ("rgb(0, 79, 144)", "rgb(0, 79, 144)"),
            ("rgb(0,79,144)", "rgb(0, 79, 144)"),
            (" rgb(0,  79,   144) ", "rgb(0, 79, 144)"),
            ("#004f90", 'rgb("#004f90")'),
            ("#ABC", 'rgb("#ABC")'),
            ("red", "red"),
            ("Navy", "navy"),
        ],
    )
    def test_converts_colors(self, value: str, expected_color: str) -> None:
        warnings: list[str] = []

        assert convert_color(value, "colors.name", warnings) == expected_color
        assert warnings == []

    @pytest.mark.parametrize(
        "value", ["hsl(0, 50%, 50%)", "rgba(0, 0, 0, 0.5)", "#12345", "crimson", ""]
    )
    def test_warns_about_colors_it_cannot_convert(self, value: str) -> None:
        warnings: list[str] = []

        assert convert_color(value, "colors.name", warnings) is None
        assert warnings == [
            f"`design.colors.name`: couldn't convert the color `{value.strip()}`."
        ]

    @pytest.mark.parametrize("color", sorted(named_colors))
    def test_named_colors_exist_in_typst(
        self, tmp_path: pathlib.Path, color: str
    ) -> None:
        main = tmp_path / "main.typ"
        main.write_text(
            f"#metadata(type({convert_color(color, 'colors.name', [])}) == color)"
            " <is-color>\n",
            encoding="utf-8",
        )

        assert json.loads(typst.query(str(main), "<is-color>", field="value", one=True))


class TestConvertDateTemplate:
    @pytest.mark.parametrize(
        ("template", "expected_text"),
        [
            ("MONTH_NAME YEAR", "May 2020"),
            ("MONTH_ABBREVIATION YEAR", "May 2020"),
            ("MONTH_ABBREVIATION. YEAR", "May. 2020"),
            ("MONTH/YEAR", "5/2020"),
            ("MONTH.YEAR", "5.2020"),
            ("MONTH_IN_TWO_DIGITS/YEAR", "05/2020"),
            ("YEAR-MONTH_IN_TWO_DIGITS", "2020-05"),
            ("YEAR-MONTH", "2020-5"),
            ("MONTH_IN_TWO_DIGITS.YEAR_IN_TWO_DIGITS", "05.20"),
            ("YEAR", "2020"),
            ("(MONTH_NAME) YEAR", "(May) 2020"),
        ],
    )
    def test_converted_templates_write_the_same_dates(
        self, tmp_path: pathlib.Path, template: str, expected_text: str
    ) -> None:
        written = evaluate_template(
            tmp_path, convert_date_template(template), "(year: 2020, month: 5), locale"
        )

        assert written == expected_text

    def test_two_digit_months_keep_two_digit_numbers(
        self, tmp_path: pathlib.Path
    ) -> None:
        written = evaluate_template(
            tmp_path,
            convert_date_template("MONTH_IN_TWO_DIGITS/YEAR"),
            "(year: 2020, month: 11), locale",
        )

        assert written == "11/2020"

    def test_is_a_typst_function_of_date_and_locale(self) -> None:
        assert convert_date_template("YEAR") == "(date, locale) => [#date.year;]"


class TestConvertValue:
    @pytest.mark.parametrize(
        ("value", "path", "expected_value"),
        [
            (True, "page.show_footer", "true"),
            (False, "page.show_footer", "false"),
            (3, "x", "3"),
            (1.5, "x", "1.5"),
            (None, "x", None),
            ("0.7in", "page.top_margin", "0.7in"),
            ("-1cm", "x", "-1cm"),
            ("1.4em", "x", "1.4em"),
            (" 10pt ", "x", "10pt"),
            ("us-letter", "page.size", '"us-letter"'),
            ("•", "entries.highlights.bullet", '"•"'),
            ('Say "hi"', "x", '"Say \\"hi\\""'),
            ("", "header.connections.separator", '""'),
            ("10", "x", '"10"'),
            ("1 cm", "x", '"1 cm"'),
            (["experience"], "sections.show_time_spans_in", '("experience",)'),
            (["a", "b"], "x", '("a", "b")'),
            ([], "x", "()"),
            ("red", "colors.name", "red"),
            ("center", "header.alignment", "center"),
            ("right", "typography.date_and_location_column_alignment", "right"),
            ("middle", "header.alignment", None),
            ("justified", "typography.alignment", '"justified"'),
            (
                {"body": "10pt", "name": "30pt"},
                "typography.font_size",
                "(body: 10pt, name: 30pt)",
            ),
            (
                {"summary": {"space_above": "0cm"}, "short_second_row": True},
                "entries",
                "(summary: (space_above: 0cm), short_second_row: true)",
            ),
            ({"a": None, "b": {"c": None}}, "x", None),
        ],
    )
    def test_converts_values_to_typst(
        self, value: Any, path: str, expected_value: str | None
    ) -> None:
        warnings: list[str] = []

        assert convert_value(value, path, warnings) == expected_value
        assert warnings == []

    def test_leaves_out_colors_it_cannot_convert(self) -> None:
        warnings: list[str] = []

        converted = convert_value(
            {"name": "crimson", "body": "rgb(0, 0, 0)"}, "colors", warnings
        )

        assert converted == "(body: rgb(0, 0, 0))"
        assert warnings == [
            "`design.colors.name`: couldn't convert the color `crimson`."
        ]


def test_alignment_options() -> None:
    assert alignment_options == {
        "header.alignment",
        "typography.date_and_location_column_alignment",
    }


class TestMigrateDesign:
    def test_an_empty_design_is_the_classic_design(self) -> None:
        migration = migrate_design({}, version="3.0.0")

        assert migration == DesignMigration(
            source=(
                "// Converted from a RenderCV 2 `design` field by `rendercv migrate`.\n"
                '#import "@preview/rendercv:3.0.0": designs\n'
                "\n"
                "#let design = designs.classic()\n"
            ),
            warnings=(),
        )

    @pytest.mark.parametrize(
        "theme",
        [
            "classic",
            "moderncv",
            "sb2nov",
            "engineeringresumes",
            "engineeringclassic",
            "harvard",
            "ink",
            "ember",
            "opal",
        ],
    )
    def test_keeps_built_in_themes(self, theme: str) -> None:
        migration = migrate_design({"theme": theme}, version="3.0.0")

        assert f"#let design = designs.{theme}()\n" in migration.source
        assert migration.warnings == ()

    def test_custom_themes_start_from_classic(self) -> None:
        migration = migrate_design({"theme": "mytheme"}, version="3.0.0")

        assert "#let design = designs.classic()\n" in migration.source
        assert migration.warnings == (
            "`design.theme` is the custom theme `mytheme`. Custom themes are Typst"
            " designs now; the migration starts from `classic`.",
        )

    def test_writes_options_as_arguments(self) -> None:
        migration = migrate_design(
            {
                "theme": "sb2nov",
                "page": {"size": "a4", "top_margin": "1cm"},
                "colors": {"name": "#ff0000"},
            },
            version="3.0.0",
        )

        assert migration.source.endswith(
            "#let design = designs.sb2nov(\n"
            '  page: (size: "a4", top_margin: 1cm),\n'
            '  colors: (name: rgb("#ff0000")),\n'
            ")\n"
        )

    def test_converts_date_templates_and_warns_about_the_rest(self) -> None:
        migration = migrate_design(
            {
                "templates": {
                    "single_date": "MONTH_NAME YEAR",
                    "date_range": "START_DATE to END_DATE",
                    "footer": "*NAME*",
                    "education_entry": {"main_column": "**INSTITUTION**"},
                }
            },
            version="3.0.0",
        )

        assert (
            "  templates: (single_date: (date, locale) =>"
            " [#locale.month_names.at(date.month - 1); #date.year;], date_range:"
            " (start, end) => [#start; to #end;]),\n" in migration.source
        )
        assert migration.warnings == (
            "`design.templates.footer`: templates with placeholders are Typst now."
            " Write it as Typst in the design's `templates` option in `design.typ`"
            " (see the docs).",
            "`design.templates.education_entry`: templates with placeholders are"
            " Typst now. Write it as Typst in the design's entry looks in"
            " `design.typ` (see the docs).",
        )

    def test_collects_color_warnings(self) -> None:
        migration = migrate_design(
            {"colors": {"name": "crimson", "links": "not a color"}}, version="3.0.0"
        )

        assert "colors" not in migration.source
        assert len(migration.warnings) == 2

    @pytest.mark.parametrize("file", v2_design_files, ids=lambda file: file.stem)
    def test_every_rendercv_2_default_design_compiles(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf, file: pathlib.Path
    ) -> None:
        design = read_yaml(file)["design"]

        migration = migrate_and_render(tmp_path, render_pdf, design)

        assert f"designs.{design['theme']}(" in migration.source
        # Only the templates that became Typst code can't be converted:
        assert all("design.templates." in warning for warning in migration.warnings)

    def test_customized_design_compiles(
        self, tmp_path: pathlib.Path, render_pdf: RenderPdf
    ) -> None:
        migrate_and_render(
            tmp_path,
            render_pdf,
            {
                "theme": "moderncv",
                "page": {"size": "a4", "show_footer": False},
                "colors": {"name": "#aa0000", "links": "blue", "body": "crimson"},
                "typography": {"font_family": "Source Sans 3", "alignment": "left"},
                "header": {"alignment": "left"},
                "sections": {"show_time_spans_in": []},
                "templates": {
                    "single_date": "YEAR-MONTH_IN_TWO_DIGITS",
                    "date_range": "START_DATE-END_DATE",
                },
            },
        )
