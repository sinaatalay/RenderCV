---
toc_depth: 2
---

# Contributing

Start with the [architecture](understanding_rendercv.md), then read the source and tests relevant to the change. The [setup guide](index.md) describes the development environment.

## Writing documentation

The developer guide teaches software engineering through RenderCV. Assume readers can follow Python but may be new to packaging, testing, templates, or Docker. Introduce each tool through the problem it solves, define unfamiliar terms when first used, and show a small example when it makes the idea concrete. Then connect the idea to the relevant code or command.

Keep the explanation short enough to follow without losing the reasoning. Remove repetition and unsupported claims; preserve the intuition a newcomer needs. Put implementation details beside the task they help explain.

## Code conventions

Use Python 3.12+ syntax and type annotations for functions, variables, and class attributes. Prefer `type` aliases, `X | Y` unions, `X | None` optionals, and type parameters such as `[T]`. Keep the source compatible with every supported Python version.

Use Google-style docstrings. Describe the behavior first; explain why or give an example when that adds information. Document arguments, return values, and exceptions that callers need to handle. Avoid comments that restate the code. Explain constraints and decisions where they affect the implementation.

Keep validation in `schema/`. A successfully validated model is the renderer's input contract: the renderer produces the requested files, and an unexpected failure propagates as a bug. Do not turn compiler errors or programming errors into input diagnostics after validation. Validate requirements involving several fields on `RenderCVModel`; validate individual fields on their owning models.

Use `uv` for Python commands and the recipes in `justfile` for routine work:

```bash
just format
just check
just test
```

Checks must pass before committing. Fix the cause of lint and type errors; use a narrowly scoped suppression only when the constraint cannot be expressed directly, and explain it.

## Fixing an issue

Read the issue and all comments, linked reports, and related code. Distinguish a reproducible bug from a feature request or usage question. For a bug, add a focused regression test and confirm that it fails before changing the implementation. Then implement the fix and rerun that test and the relevant suite. See [Testing](testing.md) for reference files, generated artifacts, and stress tests.

A pull request (PR) proposes a branch's changes for review before they are merged. Keep the change focused and target PRs at `main`. Explain the concrete problem, the resulting behavior, and the checks you ran. Credit contributors whose work you incorporate. Only use `Closes #…` when the change resolves the issue; describe any remaining scope explicitly.

## Reviewing a pull request

Read the linked issue, the full changed files on the PR branch, their callers, and the corresponding tests. Compare against the base branch and check CI. Review correctness, input validation, architecture, compatibility, and whether tests would detect the reported bug.

Make findings actionable: identify the file and line, the triggering input, the consequence, and the needed change. Distinguish blocking defects from suggestions. A passing suite is evidence for the behavior it covers, not proof that every case works.

## Triaging reports

Search open and closed issues for duplicates. Reproduce the reported behavior when enough information is available; otherwise ask for the missing input, version, or steps. Answer usage questions directly. For feature requests, explain how they fit the existing content and design model before proposing a new option.

A triage reply should state the finding, relevant code, and a concrete next step. Explain duplicate or out-of-scope decisions and link the relevant discussion. Avoid promising dates or effort estimates. In automated triage, invite the reporter to reply with `@claude` and instructions if they want a proposed fix. Apply labels or assignments only when requested by a maintainer.
