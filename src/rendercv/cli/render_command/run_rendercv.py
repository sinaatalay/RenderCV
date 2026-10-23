import contextlib
import dataclasses
import pathlib
import time
from collections.abc import Callable, Sequence
from typing import Unpack

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    YamlSource,
)
from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.renderer.pdf_png import generate_pdf, generate_png, generate_svg
from rendercv.renderer.typst import generate_typst, render_typst_source
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
    read_yaml_with_validation_errors,
)

from .progress_panel import ProgressPanel, display_path


def timed_step[T, **P](
    message: str,
    progress_panel: ProgressPanel,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """Execute function, measure timing, and update progress panel with result.

    Why:
        Each generation step (Typst, PDF, PNG, SVG) returns file paths. This wrapper
        times execution and automatically displays results in progress panel.

    Example:
        ```py
        pdf_path = timed_step(
            "Generated PDF", progress, generate_pdf, rendercv_model, typst_path
        )
        # Progress shows: ✓ 150 ms  Generated PDF: ./cv.pdf
        ```

    Args:
        message: Step description for progress display.
        progress_panel: Progress panel to update.
        func: Function to execute and time.
        args: Positional arguments for func.
        kwargs: Keyword arguments for func.

    Returns:
        Function result.
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    timing_ms = f"{(end - start) * 1000:.0f}"

    paths: list[pathlib.Path] = []
    if isinstance(result, pathlib.Path):
        paths = [result]
    elif isinstance(result, list) and result:
        if len(result) > 1:
            message = f"{message}s"
        paths = [p for p in result if isinstance(p, pathlib.Path)]

    if paths:
        progress_panel.update_progress(
            time_took=timing_ms, message=message, paths=paths
        )

    return result


@dataclasses.dataclass(frozen=True)
class InputFiles:
    """The files that a render reads.

    Args:
        input: The main YAML input file.
        design: The file of the `design` field.
        locale: The file of the `locale` field.
        settings: The file of the `settings` field.
        overlays: The files merged over the input, in order.
    """

    input: pathlib.Path
    design: pathlib.Path | None = None
    locale: pathlib.Path | None = None
    settings: pathlib.Path | None = None
    overlays: tuple[pathlib.Path, ...] = ()

    @property
    def paths(self) -> list[pathlib.Path]:
        """All the files, for watch mode to monitor."""
        files = (self.input, self.design, self.locale, self.settings, *self.overlays)
        return [path for path in files if path is not None]


def collect_input_file_paths(
    input_file_path: pathlib.Path,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    overlays: Sequence[pathlib.Path] = (),
) -> InputFiles:
    """Collect all input file paths involved in a render.

    Why:
        A render may involve multiple files: the main YAML, plus the files of
        the design/locale/settings fields and overlays, provided via CLI flags or
        referenced in settings.render_command. Watch mode needs this complete list
        to monitor all of them for changes, and the render pipeline needs the
        resolved paths to read their contents.

    Args:
        input_file_path: Path to the main YAML input file.
        design: CLI-provided design file path.
        locale: CLI-provided locale file path.
        settings: CLI-provided settings file path.
        overlays: CLI-provided overlay file paths, merged after the referenced ones.

    Returns:
        The input files.
    """
    files: dict[str, pathlib.Path | tuple[pathlib.Path, ...]] = {}
    if design:
        files["design"] = design
    if locale:
        files["locale"] = locale

    # Inspect the settings overlay before the main input: references are selected
    # per field, with CLI > settings overlay > main YAML precedence. Discovery is
    # tolerant so watch mode can monitor and recover from invalid/missing inputs;
    # the render itself reports all read/validation errors.
    selected = set(files)
    sources: list[tuple[pathlib.Path | None, YamlSource]] = [
        (settings, "settings_yaml_file"),
        (input_file_path, "main_yaml_file"),
    ]
    for source, yaml_source in sources:
        if source is None:
            continue
        with contextlib.suppress(
            OSError, RenderCVUserValidationError, RenderCVUserError
        ):
            document = read_yaml_with_validation_errors(
                source.read_text(encoding="utf-8"), yaml_source
            )
            settings_dict = document.get("settings")
            if not isinstance(settings_dict, dict):
                continue
            command = settings_dict.get("render_command")
            if not isinstance(command, dict):
                continue
            for role in ("design", "locale", "overlays"):
                if role in selected or role not in command:
                    continue
                selected.add(role)
                reference = command[role]
                if role == "overlays" and isinstance(reference, list):
                    files[role] = tuple(
                        (input_file_path.parent / item).resolve()
                        for item in reference
                        if isinstance(item, str) and item
                    )
                elif isinstance(reference, str) and reference:
                    files[role] = (input_file_path.parent / reference).resolve()

    referenced_overlays = files.get("overlays", ())
    design_file = files.get("design")
    locale_file = files.get("locale")
    return InputFiles(
        input=input_file_path,
        design=design_file if isinstance(design_file, pathlib.Path) else None,
        locale=locale_file if isinstance(locale_file, pathlib.Path) else None,
        settings=settings,
        overlays=(
            *(referenced_overlays if isinstance(referenced_overlays, tuple) else ()),
            *overlays,
        ),
    )


def run_rendercv(
    input_file_path: pathlib.Path,
    progress: ProgressPanel,
    *,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    overlays: Sequence[pathlib.Path] = (),
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> bool:
    """Execute the CV generation pipeline with progress tracking and error handling.

    Args:
        input_file_path: Path to the main YAML input file.
        progress: Progress panel for output display.
        design: CLI design overlay path.
        locale: CLI locale overlay path.
        settings: CLI settings overlay path.
        overlays: CLI overlay paths.
        kwargs: Optional YAML overlay strings, output paths, and generation flags.

    Returns:
        Whether rendering succeeded. The caller owns process exit policy.
    """
    try:
        main_yaml = input_file_path.read_text(encoding="utf-8")
        files = collect_input_file_paths(
            input_file_path, design, locale, settings, overlays
        )
        if files.settings:
            kwargs["settings_yaml_file"] = files.settings.read_text(encoding="utf-8")
        if files.design:
            kwargs["design_yaml_file"] = files.design.read_text(encoding="utf-8")
            kwargs["design_path"] = files.design
        if files.locale:
            kwargs["locale_yaml_file"] = files.locale.read_text(encoding="utf-8")
            kwargs["locale_path"] = files.locale
        kwargs["overlay_yaml_files"] = [
            (display_path(path), path.read_text(encoding="utf-8"))
            for path in files.overlays
        ]

        _, rendercv_model = timed_step(
            "Validated the input file",
            progress,
            build_rendercv_dictionary_and_model,
            main_yaml,
            input_file_path=input_file_path,
            **kwargs,
        )
    except RenderCVUserError as error:
        progress.print_user_error(error)
        return False
    except OSError as error:
        progress.print_user_error(
            RenderCVUserError(message=f"Could not read input: {error}")
        )
        return False
    except RenderCVUserValidationError as error:
        progress.print_validation_errors(error.validation_errors)
        return False

    command = rendercv_model.settings.render_command
    source = None
    if not (
        command.dont_generate_typst
        and command.dont_generate_pdf
        and command.dont_generate_png
        and command.dont_generate_svg
    ):
        source = render_typst_source(rendercv_model)
    timed_step(
        "Generated Typst",
        progress,
        generate_typst,
        rendercv_model,
        source,
    )
    timed_step(
        "Generated PDF",
        progress,
        generate_pdf,
        rendercv_model,
        source,
    )
    timed_step(
        "Generated PNG",
        progress,
        generate_png,
        rendercv_model,
        source,
    )
    timed_step(
        "Generated SVG",
        progress,
        generate_svg,
        rendercv_model,
        source,
    )
    md_path = timed_step(
        "Generated Markdown",
        progress,
        generate_markdown,
        rendercv_model,
    )
    timed_step(
        "Generated HTML",
        progress,
        generate_html,
        rendercv_model,
        md_path,
    )
    progress.finish_progress()
    return True
