from typing import Any

import pydantic
import pydantic_core

from .base import BaseModelWithoutExtraKeys
from .custom_error_types import CustomPydanticErrorTypes
from .cv.cv import Cv
from .locale.locale import Locale, default_locale
from .settings.settings import Settings


class RenderCVModel(BaseModelWithoutExtraKeys):
    """Everything in a CV's YAML file: content, language, and settings.

    Why:
        The YAML file is the control board of a CV: what it says (`cv`), in
        which language (`locale`), and how RenderCV runs (`settings`). How it
        looks is not here; that's the design, a Typst file.
    """

    # Technically, `cv` is a required field, but we don't pass it to the JSON Schema
    # so that the same schema can be used for standalone locale and settings files.
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: Cv = pydantic.Field(
        default_factory=Cv,
        title="CV",
        description="The content of the CV.",
    )
    locale: Locale = pydantic.Field(
        default_factory=default_locale,
        title="Locale",
        description="The language of the CV: its words and date formats.",
    )
    settings: Settings = pydantic.Field(
        default_factory=Settings,
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def explain_design_field(cls, data: Any) -> Any:
        """Explain where the design went if the YAML still has a `design` field.

        Why:
            RenderCV 2 set the design in the YAML. Designs are Typst files now,
            so an old `design` field deserves directions, not "unknown field".

        Args:
            data: The YAML's top-level mapping.

        Returns:
            The mapping, unchanged.
        """
        if isinstance(data, dict) and "design" in data:
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The design is not set in the YAML anymore. It's a Typst file,"
                " `design.typ`, next to your YAML file. Run `rendercv migrate` to"
                " create it from this `design` field.",
                {"loc": ("design",), "input": "..."},
            )
        return data
