from dataclasses import dataclass, field
from typing import Literal

type YamlSource = Literal[
    "main_yaml_file",
    "design_yaml_file",
    "locale_yaml_file",
    "settings_yaml_file",
]
type OverlaySourceKey = Literal["design", "locale", "settings"]
type YamlLocation = tuple[tuple[int, int], tuple[int, int]]

OVERLAY_SOURCE_TO_YAML_SOURCE: dict[OverlaySourceKey, YamlSource] = {
    "design": "design_yaml_file",
    "locale": "locale_yaml_file",
    "settings": "settings_yaml_file",
}


@dataclass
class RenderCVValidationError:
    """Structured validation error with YAML source location for error reporting.

    Why:
        Pydantic errors lack YAML file position info. This bridges the gap
        by pairing schema-level error details with YAML line/column positions
        so the CLI can display precise, user-friendly error locations.
    """

    schema_location: tuple[str, ...] | None
    yaml_location: YamlLocation | None
    yaml_source: YamlSource
    message: str
    input: str


@dataclass
class RenderCVUserError(ValueError):
    """User-facing error for recoverable problems like invalid input or missing files.

    Why:
        CLI commands catch this to display clean error panels without stack
        traces. Separating user errors from internal errors ensures only
        actionable messages reach end users.
    """

    message: str | None = field(default=None)

    def __post_init__(self) -> None:
        # The dataclass __init__ doesn't call the exception's, so without this
        # str(exc) and exc.args stay empty.
        if self.message is None:
            super().__init__()
        else:
            super().__init__(self.message)


@dataclass
class RenderCVUserValidationError(ValueError):
    """User-facing error carrying multiple structured validation errors.

    Why:
        YAML validation can produce many errors at once. Aggregating them
        in a single exception enables the CLI to display all problems in
        one pass rather than stopping at the first.
    """

    validation_errors: list[RenderCVValidationError]

    def __post_init__(self) -> None:
        super().__init__("\n".join(error.message for error in self.validation_errors))


@dataclass
class RenderCVInternalError(RuntimeError):
    """Internal error indicating a bug in RenderCV logic.

    Why:
        Distinguishes programmer errors (unreachable states, broken
        invariants) from user errors. These should never reach end users
        in normal operation and indicate code that needs fixing.
    """

    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)
