"""
The `rendercv.data.models.rendercv_data_model` module contains the `RenderCVDataModel`
data model, which is the main data model that defines the whole input file structure.
"""

import pathlib
from typing import Optional

import pydantic

from ...themes import ClassicThemeOptions
from .base import RenderCVBaseModelWithoutExtraKeys
from .curriculum_vitae import CurriculumVitae
from .design import RenderCVDesign
from .locale_catalog import LocaleCatalog
from .rendercv_settings import RenderCVSettings

INPUT_FILE_DIRECTORY: Optional[pathlib.Path] = None


class RenderCVDataModel(RenderCVBaseModelWithoutExtraKeys):
    """This class binds both the CV and the design information together."""

    # `cv` is normally required, but don't enforce it in JSON Schema to allow
    # `design` or `locale_catalog` fields to have individual YAML files.
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: CurriculumVitae = pydantic.Field(
        title="Curriculum Vitae",
        description="The data of the CV.",
    )
    design: RenderCVDesign = pydantic.Field(
        default=ClassicThemeOptions(theme="classic"),
        title="Design",
        description=(
            "The design information of the CV. The default is the classic theme."
        ),
    )
    locale_catalog: LocaleCatalog = pydantic.Field(
        default=None,  # type: ignore
        title="Locale Catalog",
        description=(
            "The locale catalog of the CV to allow the support of multiple languages."
        ),
    )
    rendercv_settings: RenderCVSettings = pydantic.Field(
        default=RenderCVSettings(),
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def update_paths(
        cls, model, info: pydantic.ValidationInfo
    ) -> Optional[RenderCVSettings]:
        """Update the paths in the RenderCV settings."""
        global INPUT_FILE_DIRECTORY  # NOQA: PLW0603

        context = info.context
        if context:
            input_file_directory = context.get("input_file_directory", None)
            INPUT_FILE_DIRECTORY = input_file_directory
        else:
            INPUT_FILE_DIRECTORY = None

        return model

    @pydantic.field_validator("locale_catalog", mode="before")
    @classmethod
    def update_locale_catalog(cls, value) -> LocaleCatalog:
        """Update the output folder name in the RenderCV settings."""
        # Somehow, we need this for `test_if_local_catalog_resets` to pass.
        if value is None:
            return LocaleCatalog()

        return value


rendercv_data_model_fields = tuple(RenderCVDataModel.model_fields.keys())
