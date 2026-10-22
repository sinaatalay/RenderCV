import pytest
import typer

from rendercv.cli.error_handler import handle_user_errors
from rendercv.exception import RenderCVUserError


class TestHandleUserErrors:
    def test_returns_function_result_on_success(self) -> None:
        @handle_user_errors
        def successful_function() -> None:
            return None

        successful_function()

    def test_catches_user_errors_and_prints_message(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        @handle_user_errors
        def failing_function() -> None:
            raise RenderCVUserError("Something went wrong")

        with pytest.raises(typer.Exit) as exc_info:
            failing_function()

        assert exc_info.value.exit_code == 1
        assert "Something went wrong" in capsys.readouterr().out

    def test_propagates_non_user_errors(self) -> None:
        @handle_user_errors
        def failing_function() -> None:
            raise ValueError("Unexpected error")

        with pytest.raises(ValueError, match="Unexpected error"):
            failing_function()
