import contextlib
import pathlib
from collections.abc import Callable

import typer
import watchdog.events
import watchdog.observers


class EventHandler(watchdog.events.FileSystemEventHandler):
    """Trigger a callback when a watched file is modified.

    Args:
        function: Callback to invoke on modification.
        watched_files: Returns the files to monitor. Called on every event, so
            files that appear later (like a new `design.typ`) are picked up.
    """

    def __init__(
        self,
        function: Callable[[], None],
        watched_files: Callable[[], list[pathlib.Path]],
    ) -> None:
        super().__init__()
        self.function = function
        self.watched_files = watched_files

    def on_any_event(self, event: watchdog.events.FileSystemEvent) -> None:
        if event.event_type not in ("modified", "created", "moved"):
            return
        changed = {str(event.src_path), str(getattr(event, "dest_path", ""))}
        # Resolved, like the paths of the events (which have no `..` in them):
        watched = {str(path.resolve()) for path in self.watched_files()}
        if not changed & watched:
            return
        with contextlib.suppress(typer.Exit):
            self.function()


def run_function_if_files_change(
    file_paths: Callable[[], list[pathlib.Path]],
    function: Callable[[], None],
) -> None:
    """Watch files and re-run function when any is modified.

    Why:
        Watch mode lets users edit a CV and see results instantly. The YAML
        file, the design, the entry types, and overlay files are all watched,
        so an edit to any of them triggers a re-render.

    Args:
        file_paths: Returns the files to watch.
        function: Zero-argument callback to invoke on file change.
    """
    # Watch parent directories (file-level watching is unreliable across platforms)
    dirs_to_schedule = {str(fp.resolve().parent) for fp in file_paths()}

    event_handler = EventHandler(function, file_paths)

    observer = watchdog.observers.Observer()
    for directory in dirs_to_schedule:
        observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    # Run immediately for the first render:
    with contextlib.suppress(typer.Exit):
        function()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
