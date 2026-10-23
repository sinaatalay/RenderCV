import functools
import inspect
from collections.abc import Callable

import rich.panel
import rich.text
import typer
from rich import print

from rendercv.exception import RenderCVUserError

from .version import warn_if_new_version_is_available


def handle_user_errors[**P](function: Callable[P, None]) -> Callable[P, None]:
    """Catch user errors and display friendly messages without stack traces.

    Why:
        CLI commands should show clean error messages for expected user errors
        (invalid YAML, missing files) while preserving stack traces for
        unexpected errors. This decorator wraps all command functions.

    Example:
        ```py
        @app.command()
        @handle_user_errors
        def my_command():
            # Any RenderCVUserError gets caught and displayed cleanly
            pass
        ```

    Args:
        function: CLI command function to wrap.

    Returns:
        Wrapped function with error handling.
    """

    signature = inspect.signature(function)

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        arguments = signature.bind(*args, **kwargs)
        quiet = arguments.arguments.get("quiet", False)
        if not quiet:
            warn_if_new_version_is_available()
        try:
            return function(*args, **kwargs)
        except RenderCVUserError as e:
            if e.message and not quiet:
                print(
                    rich.panel.Panel(
                        rich.text.Text(e.message),
                        title="[bold red]Error[/bold red]",
                        title_align="left",
                        border_style="bold red",
                    )
                )
            raise typer.Exit(code=1) from e

    return wrapper
