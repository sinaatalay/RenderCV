import pydantic

from .. import data, renderer
from . import utilities


def generate_a_typst_file(
    input_file_as_a_dict: dict,
) -> str | list[dict]:
    """
    Validate the input file given as a dictionary, generate a Typst file and return it
    as a string. If there are any validation errors, return them as a list of
    dictionaries.

    Args:
        input_file_as_a_dict: The input file as a dictionary.

    Returns:
        The Typst file as a string or a list of dictionaries that contain the error
        messages, locations, and the input values.
    """

    try:
        data_model = data.validate_input_dictionary_and_return_the_data_model(
            input_file_as_a_dict,
        )
    except pydantic.ValidationError as e:
        return utilities.parse_validation_errors(e)

    # If the `bold_keywords` field is provided in the `rendercv_settings`, make the
    # given keywords bold in the `cv.sections` field:
    if data_model.rendercv_settings and data_model.rendercv_settings.bold_keywords:
        cv_field_as_dictionary = data_model.cv.model_dump(by_alias=True)
        new_sections_field = utilities.make_given_keywords_bold_in_a_dictionary(
            cv_field_as_dictionary["sections"],
            data_model.rendercv_settings.bold_keywords,
        )
        cv_field_as_dictionary["sections"] = new_sections_field
        data_model.cv = data.models.CurriculumVitae(**cv_field_as_dictionary)

    return renderer.create_typst_contents(data_model)
