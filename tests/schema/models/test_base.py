import pydantic
import pytest

from rendercv.schema.models.base import BaseModelWithoutExtraKeys


class Strict(BaseModelWithoutExtraKeys):
    name: str = "default"


def test_base_model_without_extra_keys() -> None:
    with pytest.raises(pydantic.ValidationError) as exc_info:
        Strict.model_validate({"nmae": "x"})

    assert exc_info.value.errors()[0]["type"] == "extra_forbidden"
