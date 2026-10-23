---
toc_depth: 2
---

# GitHub Workflows

[GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) runs commands on GitHub's machines in response to events, such as opening a pull request or publishing a release. A **workflow** is a YAML file describing the event and the work to run. It contains **jobs**, each made of steps such as downloading the source, installing dependencies, and running tests.

Running checks automatically on code changes is called **continuous integration (CI)**. It gives reviewers results from a clean environment without relying only on what the author ran locally. RenderCV's workflows live in [`.github/workflows/`](https://github.com/rendercv/rendercv/tree/main/.github/workflows) and use the same `just` recipes and locked Python dependencies as local development.

## Tests

[`test.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/test.yaml) runs on pull requests, pushes to `main`, manual dispatch, and calls from other workflows. It:

1. Runs the repository's code and configuration checks and builds the documentation, treating warnings as failures.
2. Runs tests with coverage on Linux, Windows, and macOS, using Python 3.12 through 3.15.
3. Combines the coverage reports and publishes a browsable report.
4. Builds the Docker image and renders a CV without network access.

The combinations of operating system and Python version form a **test matrix**. Running the same suite in each combination catches differences such as Windows paths or Python-version behavior. The suite also checks fonts and generated schemas, examples, and the AI agent skill.

## Documentation

[`deploy-docs.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml) builds the site with `just build-docs` and deploys it to GitHub Pages on pushes to `main` or manual dispatch. See [Documentation](documentation.md) for the site configuration and preview workflow.

## Executables

[`create-executables.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/create-executables.yaml) runs manually or as part of a release. It builds standalone executables with `just create-executable` for Linux x86_64, Linux ARM64, macOS ARM64, and Windows x86_64, then uploads them as workflow artifacts.

Users can run these executables without installing Python. A workflow **artifact** is a saved output file that can be downloaded or used by a later job. See [Building distributions](project_management.md#building-distributions) for how the different delivery formats are built.

## Releases

A GitHub release identifies a published version and holds its release notes and downloadable files. Publishing one triggers [`release.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release.yaml):

1. Run the test workflow.
2. Build wheels and source distributions for `rendercv` and `rendercv-fonts`, and build the executables.
3. Attach the distributions and executables to the GitHub release.
4. Publish the Python distributions to PyPI, where Python installers download packages, skipping versions already published.
5. Build and publish the Docker image to GitHub Container Registry, where container tools download images.

The fonts package has its own version and is published only when that version changes. PyPI's **trusted publisher** configuration authorizes a particular GitHub workflow to upload a package. Before the first release from this repository, configure the fonts publisher for owner `rendercv`, repository `rendercv`, workflow `release.yaml`, and environment `release`.

After RenderCV 2.9 is released successfully, archive the former `rendercv/rendercv-fonts` repository and point its description to `packages/rendercv-fonts` here. Contributor credits are retained in the integration commit.

Typst Universe publication is separate. Follow [Publish the Typst Package](how_to/publish_typst_package.md).

## Published AI agent skill

[`publish-skill.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/publish-skill.yaml) mirrors the generated `skills/` directory to [rendercv-skill](https://github.com/rendercv/rendercv-skill) when a GitHub release is published, or on manual dispatch. It uses the `RENDERCV_SKILL_DEPLOY_KEY` repository secret. Regenerate the source with `just update-skill` before release.

## Issue and PR assistance

The Claude workflows handle issue triage, PR review, and `@claude` requests. They read the same [contribution](contributing.md) and [testing](testing.md) guides as human contributors. They require the Claude GitHub App and the `ANTHROPIC_API_KEY` repository secret. Their triggers and permissions are defined in the individual workflow files.
