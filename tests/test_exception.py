import pickle

import pytest

from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
    RenderCVValidationError,
)


@pytest.mark.parametrize(
    "error",
    [
        RenderCVUserError(message="YAML file not found"),
        RenderCVUserError("YAML file not found"),
        RenderCVInternalError(message="YAML file not found"),
    ],
)
def test_message_is_the_exception_text(error):
    assert str(error) == "YAML file not found"
    assert error.args == ("YAML file not found",)


def test_user_error_without_message():
    error = RenderCVUserError()

    assert error.message is None
    assert str(error) == ""
    assert error.args == ()


def test_validation_error_text_lists_messages():
    errors = [
        RenderCVValidationError(
            schema_location=("cv", "name"),
            yaml_location=None,
            yaml_source="main_yaml_file",
            message=message,
            input="",
        )
        for message in ("first problem", "second problem")
    ]
    error = RenderCVUserValidationError(validation_errors=errors)

    assert str(error) == "first problem\nsecond problem"
    assert error.validation_errors == errors


@pytest.mark.parametrize(
    "error",
    [RenderCVUserError(message="boom"), RenderCVInternalError(message="boom")],
)
def test_survives_pickling(error):
    restored = pickle.loads(pickle.dumps(error))

    assert type(restored) is type(error)
    assert restored.message == "boom"
    assert str(restored) == "boom"
