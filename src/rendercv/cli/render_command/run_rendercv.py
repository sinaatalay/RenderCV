import contextlib
import pathlib
import time
from collections.abc import Callable
from typing import Any, Unpack

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.outputs import (
    generate_html,
    generate_markdown,
    generate_pdf,
    generate_png,
    generate_typst,
)
from rendercv.renderer.project import (
    default_design_file_name,
    default_entries_file_name,
    load_project,
)
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    read_yaml_with_validation_errors,
)

from .progress_panel import ProgressPanel


def timed_step[T, **P](
    message: str,
    progress_panel: ProgressPanel,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """Execute function, measure timing, and update progress panel with result.

    Why:
        Each generation step (Typst, PDF, PNG) returns file paths. This wrapper
        times execution and automatically displays results in progress panel.

    Example:
        ```py
        pdf_path = timed_step("Generated PDF", progress, generate_pdf, project)
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


def collect_input_file_paths(
    input_file_path: pathlib.Path,
    *,
    design: pathlib.Path | None = None,
    entries: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
) -> dict[str, pathlib.Path]:
    """Collect every file a render reads, for watch mode.

    Why:
        A CV is the YAML file plus its design, entry types, and optional locale
        and settings files. Watch mode re-renders when any of them changes.

    Args:
        input_file_path: The CV's YAML file.
        design: The design file given on the command line.
        entries: The entries file given on the command line.
        locale: The locale overlay file given on the command line.
        settings: The settings overlay file given on the command line.

    Returns:
        Roles ("input", "design", ...) mapped to absolute paths of files that
        exist.
    """
    files: dict[str, pathlib.Path] = {"input": input_file_path}
    main: Any = None
    # Watch mode should keep going if the YAML is empty, broken, or missing right
    # now (some editors delete and recreate a file when saving it):
    with contextlib.suppress(RenderCVUserError, RenderCVUserValidationError, OSError):
        main = read_yaml_with_validation_errors(
            input_file_path.read_text(encoding="utf-8"), "main_yaml_file"
        )
    settings_field = main.get("settings") if isinstance(main, dict) else None
    render_command_field = (
        settings_field.get("render_command")
        if isinstance(settings_field, dict)
        else None
    )
    render_command: dict[str, Any] = (
        render_command_field if isinstance(render_command_field, dict) else {}
    )

    def from_yaml(key: str, default_name: str | None) -> pathlib.Path | None:
        value = render_command.get(key)
        if value:
            return input_file_path.parent / str(value)
        if default_name:
            return input_file_path.parent / default_name
        return None

    candidates = {
        "design": design or from_yaml("design", default_design_file_name),
        "entries": entries or from_yaml("entries", default_entries_file_name),
        "locale": locale or from_yaml("locale", None),
        "settings": settings,
    }
    for role, path in candidates.items():
        if path is not None and path.is_file():
            files[role] = path.absolute()
    return files


def run_rendercv(
    input_file_path: pathlib.Path,
    progress: ProgressPanel,
    *,
    design: pathlib.Path | None = None,
    entries: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> None:
    """Render a CV, reading every input anew, with progress and error display.

    Args:
        input_file_path: The CV's YAML file.
        progress: Progress panel for output display.
        design: A design file given on the command line.
        entries: An entries file given on the command line.
        locale: A locale overlay file given on the command line.
        settings: A settings overlay file given on the command line.
        kwargs: Output paths, generation flags, and overrides.
    """
    try:
        overlays = collect_input_file_paths(
            input_file_path, locale=locale, settings=settings
        )
        if "locale" in overlays:
            kwargs["locale_yaml_file"] = overlays["locale"].read_text(encoding="utf-8")
        if "settings" in overlays:
            kwargs["settings_yaml_file"] = overlays["settings"].read_text(
                encoding="utf-8"
            )
        project = timed_step(
            "Validated the input file",
            progress,
            load_project,
            input_file_path,
            design_file=design,
            entries_file=entries,
            **kwargs,
        )
        timed_step("Generated Typst", progress, generate_typst, project)
        timed_step("Generated PDF", progress, generate_pdf, project)
        timed_step("Generated PNG", progress, generate_png, project)
        timed_step("Generated Markdown", progress, generate_markdown, project)
        timed_step("Generated HTML", progress, generate_html, project)
        progress.finish_progress()
    except RenderCVUserError as e:
        progress.print_user_error(e)
    except OSError as e:
        progress.print_user_error(RenderCVUserError(f"OS Error: {e}"))
    except RenderCVUserValidationError as e:
        progress.print_validation_errors(e.validation_errors)
