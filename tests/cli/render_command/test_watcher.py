import pathlib
import threading
from collections.abc import Callable, Iterator
from unittest.mock import MagicMock

import pytest
import typer
import watchdog.events
import watchdog.observers
from watchdog.observers.api import BaseObserver

from rendercv.cli.render_command import watcher
from rendercv.cli.render_command.run_rendercv import collect_input_file_paths
from rendercv.cli.render_command.watcher import EventHandler

type EventFactory = Callable[[str], watchdog.events.FileSystemEvent]


class TestEventHandler:
    @pytest.mark.parametrize(
        "create_event",
        [
            watchdog.events.FileModifiedEvent,
            watchdog.events.FileCreatedEvent,
            # Editors that save by writing a temporary file and renaming it:
            lambda path: watchdog.events.FileMovedEvent(path + ".tmp", path),
        ],
    )
    def test_calls_function_when_watched_file_changes(
        self, tmp_path: pathlib.Path, create_event: EventFactory
    ) -> None:
        function = MagicMock()
        handler = EventHandler(function, lambda: [tmp_path / "cv.yaml"])

        handler.dispatch(create_event(str(tmp_path / "cv.yaml")))

        function.assert_called_once()

    @pytest.mark.parametrize(
        ("create_event", "file_name"),
        [
            (watchdog.events.FileModifiedEvent, "other.yaml"),
            (watchdog.events.FileDeletedEvent, "cv.yaml"),
            (watchdog.events.FileOpenedEvent, "cv.yaml"),
        ],
    )
    def test_ignores_other_events(
        self, tmp_path: pathlib.Path, create_event: EventFactory, file_name: str
    ) -> None:
        function = MagicMock()
        handler = EventHandler(function, lambda: [tmp_path / "cv.yaml"])

        handler.dispatch(create_event(str(tmp_path / file_name)))

        function.assert_not_called()

    def test_reads_watched_files_on_every_event(self, tmp_path: pathlib.Path) -> None:
        watched_files = [tmp_path / "cv.yaml"]
        function = MagicMock()
        handler = EventHandler(function, lambda: watched_files)

        # A `design.typ` created after watching started:
        watched_files.append(tmp_path / "design.typ")
        handler.dispatch(watchdog.events.FileCreatedEvent(str(tmp_path / "design.typ")))

        function.assert_called_once()

    def test_matches_paths_with_parent_folder_references(
        self, tmp_path: pathlib.Path
    ) -> None:
        function = MagicMock()
        handler = EventHandler(
            function, lambda: [tmp_path / "folder" / ".." / "design.typ"]
        )

        handler.dispatch(
            watchdog.events.FileModifiedEvent(str(tmp_path / "design.typ"))
        )

        function.assert_called_once()

    def test_suppresses_typer_exit(self, tmp_path: pathlib.Path) -> None:
        function = MagicMock(side_effect=typer.Exit(code=1))
        handler = EventHandler(function, lambda: [tmp_path / "cv.yaml"])

        handler.dispatch(watchdog.events.FileModifiedEvent(str(tmp_path / "cv.yaml")))

        function.assert_called_once()


@pytest.fixture
def observers(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[BaseObserver]]:
    # Real observers, stopped after the test so their threads end:
    created: list[BaseObserver] = []
    original_observer = watchdog.observers.Observer

    def create_observer() -> BaseObserver:
        observer = original_observer()
        created.append(observer)
        return observer

    monkeypatch.setattr(watcher.watchdog.observers, "Observer", create_observer)
    yield created
    for observer in created:
        observer.stop()


class CallCounter:
    """Counts calls and lets a test wait for the next one."""

    def __init__(self, side_effect: Exception | None = None) -> None:
        self.count: int = 0
        self.side_effect: Exception | None = side_effect
        self.called: threading.Event = threading.Event()

    def __call__(self) -> None:
        self.count += 1
        self.called.set()
        if self.side_effect is not None:
            raise self.side_effect

    def wait_for_call_after(self, action: Callable[[], object]) -> bool:
        # File system events can be late or merged, so retry the action a few times:
        for _ in range(20):
            self.called.clear()
            action()
            if self.called.wait(timeout=0.5):
                return True
        return False


def start_watching(
    file_paths: Callable[[], list[pathlib.Path]], counter: CallCounter
) -> None:
    thread = threading.Thread(
        target=watcher.run_function_if_files_change,
        args=(file_paths, counter),
        daemon=True,
    )
    thread.start()
    assert counter.called.wait(timeout=10), "The function didn't run at start."


class TestRunFunctionIfFilesChange:
    def test_runs_function_at_start_and_stops_on_keyboard_interrupt(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        observer = MagicMock()
        # The first join is interrupted, the one after stopping returns:
        observer.join.side_effect = [KeyboardInterrupt, None]
        monkeypatch.setattr(
            watcher.watchdog.observers, "Observer", MagicMock(return_value=observer)
        )
        function = MagicMock(side_effect=typer.Exit(code=1))

        watcher.run_function_if_files_change(lambda: [tmp_path / "cv.yaml"], function)

        function.assert_called_once()
        observer.schedule.assert_called_once()
        assert observer.schedule.call_args.args[1] == str(tmp_path.resolve())
        observer.stop.assert_called_once()

    def test_schedules_folder_of_every_file(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        observer = MagicMock()
        observer.join.side_effect = [KeyboardInterrupt, None]
        monkeypatch.setattr(
            watcher.watchdog.observers, "Observer", MagicMock(return_value=observer)
        )
        files = [tmp_path / "cv.yaml", tmp_path / "cv" / "../design.typ"]
        files += [tmp_path / "styles" / "entries.typ"]

        watcher.run_function_if_files_change(lambda: files, MagicMock())

        scheduled = {call.args[1] for call in observer.schedule.call_args_list}
        assert scheduled == {
            str(tmp_path.resolve()),
            str((tmp_path / "styles").resolve()),
        }

    @pytest.mark.parametrize("changed_file", ["cv.yaml", "design.typ", "entries.typ"])
    def test_reruns_function_when_an_input_file_changes(
        self,
        tmp_path: pathlib.Path,
        observers: list[BaseObserver],  # noqa: ARG002
        changed_file: str,
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        (tmp_path / "design.typ").write_text("// design", encoding="utf-8")
        (tmp_path / "entries.typ").write_text("// entries", encoding="utf-8")
        counter = CallCounter()

        start_watching(
            lambda: list(collect_input_file_paths(yaml_file).values()), counter
        )

        assert counter.wait_for_call_after(
            lambda: (tmp_path / changed_file).write_text(
                f"cv:\n  name: Edit {counter.count}\n", encoding="utf-8"
            )
        )

    def test_reruns_function_when_design_file_is_created(
        self,
        tmp_path: pathlib.Path,
        observers: list[BaseObserver],  # noqa: ARG002
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        counter = CallCounter()

        start_watching(
            lambda: list(collect_input_file_paths(yaml_file).values()), counter
        )

        assert counter.wait_for_call_after(
            lambda: (tmp_path / "design.typ").write_text(
                f"// design {counter.count}", encoding="utf-8"
            )
        )

    def test_keeps_watching_after_function_exits(
        self,
        tmp_path: pathlib.Path,
        observers: list[BaseObserver],  # noqa: ARG002
    ) -> None:
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        counter = CallCounter(side_effect=typer.Exit(code=1))

        start_watching(lambda: [yaml_file], counter)

        for edit in range(2):
            assert counter.wait_for_call_after(
                lambda edit=edit: yaml_file.write_text(
                    f"cv:\n  name: Edit {edit} {counter.count}\n", encoding="utf-8"
                )
            )
