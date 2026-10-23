import pytest


@pytest.fixture
def update_testdata(request):
    # These tests exercise the comparison itself, including under --update-testdata.
    return getattr(request, "param", False)


@pytest.fixture
def testdata_dir(tmp_path):
    directory = tmp_path / "references"
    directory.mkdir()
    return directory


@pytest.mark.parametrize("different_page", [1, 2])
def test_every_page_must_match(
    compare_file_with_reference, testdata_dir, different_page
):
    for page in (1, 2):
        (testdata_dir / f"cv_{page}.png").write_bytes(b"reference")

    def generate(path):
        for page in (1, 2):
            content = b"changed" if page == different_page else b"reference"
            path.with_name(f"cv_{page}.png").write_bytes(content)

    assert not compare_file_with_reference(generate, "cv.png")


def test_pairs_files_by_name(compare_file_with_reference, testdata_dir):
    for page in (2, 1):
        (testdata_dir / f"cv_{page}.png").write_bytes(str(page).encode())

    def generate(path):
        for page in (1, 2):
            path.with_name(f"cv_{page}.png").write_bytes(str(page).encode())

    assert compare_file_with_reference(generate, "cv.png")


@pytest.mark.parametrize("update_testdata", [True], indirect=True)
def test_updating_references_removes_pages_that_no_longer_exist(
    compare_file_with_reference, testdata_dir
):
    for name in ("cv_1.png", "cv_2.png", "unrelated.png"):
        (testdata_dir / name).write_bytes(b"old")

    def generate(path):
        path.with_name("cv_1.png").write_bytes(b"new")

    assert compare_file_with_reference(generate, "cv.png")
    assert (testdata_dir / "cv_1.png").read_bytes() == b"new"
    assert not (testdata_dir / "cv_2.png").exists()
    assert (testdata_dir / "unrelated.png").read_bytes() == b"old"
