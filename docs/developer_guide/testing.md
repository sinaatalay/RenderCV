---
toc_depth: 2
---

# Testing

Tests check if your code does what it's supposed to do. Every time you change something, you need to verify it still works. Instead of manually checking everything, you can write test code once and rerun it after each change.

Here's a simple example:

```python
def sum(a, b):
    return a + b

def test_sum():
    assert sum(2, 3) == 5
    assert sum(-1, 1) == 0
    assert sum(0, 0) == 0
```

If you change something in `sum`, you can run `test_sum` again to see if it's still working.

All of the tests of RenderCV are written in [`tests/`](https://github.com/rendercv/rendercv/tree/main/tests) directory.

## [`pytest`](https://github.com/pytest-dev/pytest): Testing Framework

`pytest` is a Python library that provides utilities to write and run tests.

**How does it work?** When you run `pytest`, it searches for files matching `test_*.py` in the `tests/` directory and executes all functions starting with `test_`.

## Running RenderCV Tests

Whenever you make changes to RenderCV's source code, run the tests to ensure everything still works. If all tests pass, your changes didn't break anything.

```bash
just test
```

## How the Tests Are Organized

Tests mirror the code they test:

- Python: `src/rendercv/schema/models/cv/section.py` is tested in `tests/schema/models/cv/test_section.py`.
- Typst: RenderCV's Typst package in `typst/` is tested in `tests/typst/`, which mirrors `typst/` the same way.

[`tests/test_tests.py`](https://github.com/rendercv/rendercv/blob/main/tests/test_tests.py) checks that every test file has a matching source file, so tests don't drift away from the code.

## Reference File Comparison

Some tests check RenderCV's output (PDFs, PNGs, Typst, Markdown, HTML) by comparing it against reference files:

1. Tests generate output files by running RenderCV
2. Generated files are compared against reference files in the `testdata/` folder next to the test
3. If they match exactly, the test passes. Any difference fails the test.

### Updating Reference Files

You fix a bug that changes RenderCV's output. Tests fail because the new output doesn't match old reference files.

**This is expected.** You intentionally changed the output. You need to update the reference files:

```bash
just update-testdata
```

!!! warning
    **Manually verify new reference files before committing.** These become the source of truth. If you commit broken reference files, tests will pass even when RenderCV produces bad output. Always check generated PDFs and PNGs carefully.

## [`pytest-cov`](https://github.com/pytest-dev/pytest-cov): Coverage Plugin for `pytest`

Coverage is a measure of which code lines are executed when tests run. If tests execute a line, it's included in coverage. If tests execute all lines in `src/rendercv/`, coverage is 100%.

**Why does it matter?** Coverage reports show you which parts of your code aren't tested yet, so you know where to write more tests.

Run tests with coverage:

```bash
just test-coverage
```

This generates two outputs:

- **Terminal:** Overall coverage percentage
- **HTML report:** Open `htmlcov/index.html` to see exactly which lines are covered (green) and which aren't (red)
