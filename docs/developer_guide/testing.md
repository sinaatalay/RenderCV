---
toc_depth: 2
---

# Testing

A test runs code and checks its result against an expectation. This records how the code should behave and catches changes that break that behavior. RenderCV uses [pytest](https://docs.pytest.org/) to find and run functions named `test_...` in `tests/`, whose paths mirror `src/rendercv/`.

For example, this test expresses the rule that an overlay replaces a whole list:

```python
from rendercv.schema.override_dictionary import merge_overlay


def test_overlay_replaces_a_list():
    data = {"items": ["first", "second"]}
    merge_overlay(data, {"items": ["replacement"]})
    assert data["items"] == ["replacement"]
```

The `assert` fails if the actual result differs. For a bug fix, first make a test fail on the reported input, then change the implementation. That confirms the test can detect the bug and protects against its return: a **regression**.

## Run the tests

```bash
just test
just test-coverage
```

**Coverage** measures which statements ran during testing. Open `htmlcov/index.html` to find code the tests did not execute. Executing a line does not establish that its result was checked correctly, so coverage helps locate gaps but does not prove correctness.

While developing, run the relevant file and stop at its first failure with `-x`:

```bash
uv run --frozen --all-extras pytest tests/renderer/templater/test_date.py -x
```

## Write behavior tests

Assert the expected result or error, rather than the sequence of internal calls. Prefer real parsing, validation, and rendering. A **mock** replaces a dependency with a controlled substitute; use one for an external service when the test should not make a network request. Test file operations with temporary files.

A pytest **fixture** supplies setup through a test's arguments. For example, `tmp_path` supplies a separate temporary directory for each test. Put shared fixtures in the nearest common `conftest.py`, which pytest discovers automatically. Keep simple values inline.

Name a single test after the function or class it exercises. Group multiple tests under `TestFunctionName` or `TestClassName`, with method names describing expected behavior. Use `pytest.mark.parametrize` to run the same test with several input/expected-result pairs.

Choose boundary cases relevant to the change: missing fields, empty lists, Unicode, multiline content, nested entries, or paths outside the working directory. Pipeline tests should check that invalid input fails during validation and unexpected renderer failures propagate.

## Compare rendered output

Renderer tests compare generated files with saved **reference files** in `tests/renderer/testdata/`. These record the output we previously inspected and accepted. A difference in any expected page fails the comparison, which catches layout changes that small assertions can miss.

When output changes intentionally, run:

```bash
just update-testdata
```

Inspect the changed Typst, Markdown, HTML, PDFs, and images before committing them. Updating references accepts the new output, so doing it without inspection could accept a bug. Keep focused regression assertions alongside these broad comparisons.

Tests also check that generated schemas, examples, and the AI agent skill match their source. Regenerate the artifacts affected by your change.

## Test properties across many inputs

An example test checks particular values. A **property-based test** checks a rule across generated inputs. For example, applying keyword bolding twice should have the same result as applying it once.

[Hypothesis](https://hypothesis.readthedocs.io/) generates cases from rules called strategies. If it finds a failure, it tries to reduce the input to a smaller example that still fails. RenderCV's strategies combine formatting, links, code, Typst expressions, lists, multiline values, and missing placeholders, revealing interactions that hand-picked examples can miss.

`just test` uses the normal profile. For content-pipeline changes, use the stress profile:

```bash
HYPOTHESIS_PROFILE=stress uv run --frozen --all-extras pytest tests/renderer/templater
```

It requests 1,500 examples per property; finite input sets can run out sooner. Preserve useful failing examples as focused regression tests after fixing the bug.
