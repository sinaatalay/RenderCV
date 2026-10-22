import pathlib

import pytest
import typer

from rendercv.cli.render_command.progress_panel import (
    CompletedStep,
    ProgressPanel,
    format_validation_error_location,
)
from rendercv.exception import (
    RenderCVUserError,
    RenderCVValidationError,
    YamlLocation,
    YamlSource,
)


def make_error(
    schema_location: tuple[str, ...] | None,
    yaml_location: YamlLocation | None,
    yaml_source: YamlSource = "main_yaml_file",
) -> RenderCVValidationError:
    return RenderCVValidationError(
        schema_location=schema_location,
        yaml_location=yaml_location,
        yaml_source=yaml_source,
        input="123",
        message="Invalid value",
    )


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            make_error(("cv", "email"), ((2, 3), (2, 8))),
            "cv.email\n[dim](line 2)[/dim]",
        ),
        (
            make_error(("cv", "email"), ((2, 3), (4, 8))),
            "cv.email\n[dim](lines 2-4)[/dim]",
        ),
        (
            make_error(
                ("settings", "current_date"), ((3, 1), (3, 5)), "settings_yaml_file"
            ),
            "settings.current_date\n[dim](settings file, line 3)[/dim]",
        ),
        (
            make_error(("locale", "language"), None, "locale_yaml_file"),
            "locale.language\n[dim](locale file)[/dim]",
        ),
        (make_error(("cv", "name"), None), "cv.name"),
        # YAML syntax errors have no schema location:
        (make_error(None, ((3, 7), (3, 7))), "line 3"),
        (make_error(None, ((3, 7), (3, 7)), "locale_yaml_file"), "locale file, line 3"),
        (make_error(None, None, "settings_yaml_file"), "settings file"),
        (make_error(None, None), "input file"),
    ],
)
def test_format_validation_error_location(
    error: RenderCVValidationError, expected: str
) -> None:
    assert format_validation_error_location(error) == expected


class TestProgressPanel:
    def test_update_progress_adds_step(self) -> None:
        panel = ProgressPanel(quiet=True)
        paths = [pathlib.Path.cwd() / "page_1.png", pathlib.Path.cwd() / "page_2.png"]

        panel.update_progress("250", "Generated PNGs", paths)

        assert panel.completed_steps == [CompletedStep("250", "Generated PNGs", paths)]

    def test_finish_progress_clears_steps(self) -> None:
        panel = ProgressPanel(quiet=True)
        panel.update_progress("100", "Generated PDF", [pathlib.Path.cwd() / "cv.pdf"])

        panel.finish_progress()

        assert panel.completed_steps == []

    def test_clear_clears_steps(self) -> None:
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.extend(
            [CompletedStep("100", "Step 1", []), CompletedStep("200", "Step 2", [])]
        )

        panel.clear()

        assert panel.completed_steps == []

    def test_prints_nothing_when_quiet(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with ProgressPanel(quiet=True) as panel:
            panel.update_progress(
                "100", "Generated PDF", [pathlib.Path.cwd() / "a.pdf"]
            )
            panel.finish_progress()

        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize(
        "paths",
        [
            [],
            [pathlib.Path.cwd() / "cv.pdf"],
            # Paths outside the current folder are shown as they are:
            [pathlib.Path("/elsewhere/cv_1.png"), pathlib.Path("/elsewhere/cv_2.png")],
        ],
    )
    def test_shows_steps(
        self, paths: list[pathlib.Path], capsys: pytest.CaptureFixture[str]
    ) -> None:
        with ProgressPanel() as panel:
            panel.update_progress("100", "Generated files", paths)
            panel.finish_progress()

        output = capsys.readouterr().out
        assert "Your CV is ready" in output
        assert "Generated files" in output

    @pytest.mark.parametrize("message", ["Test error message", None])
    def test_print_user_error_exits_with_code_1(self, message: str | None) -> None:
        panel = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_user_error(RenderCVUserError(message=message))

        assert exc_info.value.exit_code == 1

    def test_print_validation_errors_exits_with_code_1(self) -> None:
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(CompletedStep("100", "Test", []))
        errors = [
            make_error(("cv", "name"), ((1, 1), (1, 1))),
            make_error(None, ((3, 7), (3, 7))),
        ]

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_validation_errors(errors)

        assert exc_info.value.exit_code == 1
        assert panel.completed_steps == []
