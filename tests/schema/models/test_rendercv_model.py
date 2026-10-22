import pydantic
import pytest

from rendercv.schema.models.custom_error_types import CustomPydanticErrorTypes
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.locale.locale import default_locale
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


class TestRenderCVModel:
    def test_every_part_has_a_default(self) -> None:
        model = RenderCVModel()

        assert model.cv == Cv()
        assert model.locale == default_locale()
        assert model.settings == Settings()

    def test_explains_where_the_design_went(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            RenderCVModel.model_validate({"cv": {}, "design": {"theme": "classic"}})

        (error,) = exc_info.value.errors()
        assert error["type"] == CustomPydanticErrorTypes.other.value
        assert "Run `rendercv migrate`" in error["msg"]
        # Where the error is, for the error table:
        assert error["ctx"] == {"loc": ("design",), "input": "..."}

    def test_rejects_unknown_fields(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            RenderCVModel.model_validate({"cvv": {}})

        assert exc_info.value.errors()[0]["loc"] == ("cvv",)

    def test_json_schema_requires_nothing(self) -> None:
        # So the same schema checks standalone locale and settings files:
        assert RenderCVModel.model_json_schema()["required"] == []
