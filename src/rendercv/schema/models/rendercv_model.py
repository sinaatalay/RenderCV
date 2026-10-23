import pathlib

import pydantic
import pydantic_core

from ..template_validation import validate_templates
from .base import BaseModelWithoutExtraKeys
from .cv.cv import Cv
from .design.classic_theme import ClassicTheme
from .design.design import Design
from .locale.locale import EnglishLocale, Locale
from .settings.settings import Settings
from .validation_context import get_input_file_path


class RenderCVModel(BaseModelWithoutExtraKeys):
    """Top-level model representing a complete RenderCV configuration.

    Why:
        This is the root of the entire data model, combining CV content,
        design theme, locale translations, and rendering settings into a
        single validated structure. All rendering pipeline stages operate
        on this unified model.
    """

    # Technically, `cv` is a required field, but we don't pass it to the JSON Schema
    # so that the same schema can be used for standalone design, locale, and settings
    # files.
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: Cv = pydantic.Field(
        default_factory=Cv,
        title="CV",
        description="The content of the CV.",
    )
    design: Design = pydantic.Field(
        default_factory=ClassicTheme,
        title="Design",
        description=(
            "The design information of the CV. The default is the `classic` theme."
        ),
    )
    locale: Locale = pydantic.Field(
        default_factory=EnglishLocale,
        title="Locale Catalog",
        description=(
            "The locale catalog of the CV to allow the support of multiple languages."
        ),
    )
    settings: Settings = pydantic.Field(
        default_factory=Settings,
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    _input_file_path: pathlib.Path | None = pydantic.PrivateAttr(default=None)

    @pydantic.model_validator(mode="after")
    def set_input_file_path(self, info: pydantic.ValidationInfo) -> "RenderCVModel":
        """Store input file path in private attribute for path resolution.

        Why:
            Photo paths and other relative references need input file location
            for resolution. Private attribute stores this after validation for
            downstream processing.

        Args:
            info: Validation context containing input file path.

        Returns:
            Model instance with _input_file_path set.
        """
        self._input_file_path = get_input_file_path(info)
        return self

    @pydantic.model_validator(mode="after")
    def validate_document(self) -> "RenderCVModel":
        """Validate requirements that depend on more than one top-level field.

        Returns:
            The validated document.
        """
        if (
            not self.settings.render_command.dont_generate_pdf
            and "ua-1" in self.settings.pdf_standards
            and not (self.cv.name and self.cv.name.strip())
        ):
            raise pydantic.ValidationError.from_exception_data(
                type(self).__name__,
                [
                    {
                        "type": pydantic_core.PydanticCustomError(
                            "rendercv_other_error",
                            "PDF/UA-1 requires a main heading. Add `cv.name`, or set"
                            " `settings.pdf_standards` to `[]` for an unnamed PDF.",
                        ),
                        "loc": ("cv", "name"),
                        "input": self.cv.name,
                    }
                ],
            )
        directory = (
            self._input_file_path.parent
            if self._input_file_path
            else pathlib.Path.cwd()
        )
        command = self.settings.render_command
        formats: set[str] = set()
        if not all(
            (
                command.dont_generate_typst,
                command.dont_generate_pdf,
                command.dont_generate_png,
                command.dont_generate_svg,
            )
        ):
            formats.add("typst")
        if not command.dont_generate_markdown:
            formats.add("markdown")
            if not command.dont_generate_html:
                formats.add("html")
        validate_templates(directory, self.design.theme, formats)
        return self
