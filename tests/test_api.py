import rendercv


def test_create_contents_of_a_typst_file(input_file_path):
    yaml_string = input_file_path.read_text()
    assert isinstance(rendercv.create_contents_of_a_typst_file(yaml_string), str)
