from itertools import combinations_with_replacement
from typing import get_args

import pydantic
import pytest
import typst

from rendercv.schema.models.settings.settings import PdfStandard, Settings


@pytest.mark.parametrize(
    "standards", list(combinations_with_replacement(get_args(PdfStandard.__value__), 2))
)
def test_pdf_standards_validation_agrees_with_the_compiler(standards):
    # Compare against the compiler so dependency upgrades expose changed constraints.
    source = b'#set document(title: "Title")\n= Name'
    try:
        typst.compile(source, pdf_standards=list(standards))
    except typst.TypstError as error:
        if "PDF standards error" not in str(error):
            raise
        with pytest.raises(pydantic.ValidationError) as validation:
            Settings(pdf_standards=list(standards))
        assert validation.value.errors()[0]["loc"] == ("pdf_standards",)
    else:
        assert Settings(pdf_standards=list(standards)).pdf_standards == list(standards)


def test_combines_a_version_with_archival_and_accessibility_standards():
    standards = ["1.7", "a-2b", "ua-1"]
    assert (
        Settings.model_validate({"pdf_standards": standards}).pdf_standards == standards
    )
