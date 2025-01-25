"""
The `rendercv.api.functions` package contains the basic functions that are used to
interact with the RenderCV.
"""

import pydantic

from .. import data, renderer


def create_contents_of_a_typst_file(
    yaml_file_as_string: str,
) -> str | list[dict]:
    """
    Validate the input file given as a string, generate a Typst file and return it as a
    string. If there are any validation errors, return them as a list of dictionaries.

    Args:
        yaml_file_as_string: The input file as a string.

    Returns:
        The Typst file as a string or a list of dictionaries that contain the error
            messages, locations, and the input values.
    """

    try:
        input_file_as_a_dict = data.read_a_yaml_file(yaml_file_as_string)
        data_model = data.validate_input_dictionary_and_return_the_data_model(
            input_file_as_a_dict,
        )
    except pydantic.ValidationError as e:
        return data.parse_validation_errors(e)

    return renderer.create_contents_of_a_typst_file(data_model)
