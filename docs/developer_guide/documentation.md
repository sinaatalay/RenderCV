---
toc_depth: 3
---

# Documentation

## The Goal

We want documentation at `docs.rendercv.com`, a proper website with navigation, search, theming, and interactive features.

**What is a website?** A collection of HTML, CSS, and JavaScript files. Browsers download these files and render them as the pages you see. To have a website, you need:

1. HTML/CSS/JavaScript files
2. A server hosting those files
3. A domain (e.g. `docs.rendercv.com`) pointing to that server

**The problem:** We don't want to develop a web app (writing HTML/CSS/JavaScript). We just want to put some content online.

What if we could write content in Markdown and use some software to automatically generate HTML/CSS/JavaScript files from it?

**The solution:** [MkDocs](https://github.com/mkdocs/mkdocs) with [Material theme](https://github.com/squidfunk/mkdocs-material). You write Markdown in `docs/`, MkDocs generates HTML/CSS/JavaScript, and GitHub Pages hosts it at `docs.rendercv.com`.

Tools like MkDocs exist because documentation sites follow a stable, well-understood pattern. They aren’t open-ended web applications with unique interfaces or behaviors; they’re a specific kind of website with predictable needs: structured pages, cross-page navigation, search, consistent styling, and readable content.

Once a pattern becomes that well defined, entire ecosystems form around it. Just as you reach for Python rather than designing a new programming language, you reach for MkDocs rather than hand-assembling HTML, CSS, and JavaScript files for a documentation site.

## Configuration: [`mkdocs.yaml`](https://github.com/rendercv/rendercv/blob/main/mkdocs.yaml)

`mkdocs.yaml` controls how MkDocs builds the website:

- **Site metadata:** name, description, repository
- **Theme:** Material theme with colors and features
- **Navigation:** sidebar structure
- **Plugins:** see below

## Plugins

MkDocs plugins extend functionality beyond Markdown → HTML conversion.

### [`mkdocstrings`](https://github.com/mkdocstrings/mkdocstrings): API Reference

Generates the API reference from Python docstrings. The entire [API Reference](../api_reference/index.md) section is auto-generated from `src/rendercv/`.

### [`mkdocs-macros-plugin`](https://mkdocs-macros-plugin.readthedocs.io/): Dynamic Content

Lets you inject code-generated values into Markdown. [`docs/docs_templating.py`](https://github.com/rendercv/rendercv/blob/main/docs/docs_templating.py) runs during the build. It reads values directly from RenderCV's code and Typst package and exposes them as variables (written `{$ raw $}<< variable >>{$ endraw $}` in the pages), so the docs can't drift from the code:

- The lists of designs, locales, social networks, and fonts.
- The standard entry types and their fields, read from Typst exactly like `rendercv render` reads them. The [Entry Types](../user_guide/entry_types.md) page is built from them.
- The design options and each design's defaults, copied from the Typst sources in `typst/designs/` into the [Design](../user_guide/design.md) page.
- The sample `design.typ` and `entries.typ` that `rendercv new` creates.

## Entry Type Figures

The [Entry Types](../user_guide/entry_types.md) page shows example images of each standard entry type rendered in each design.

These are auto-generated PNG images in `docs/assets/images/<design>/`. Run `just update-entry-figures` to regenerate them from [`docs/user_guide/sample_entries.yaml`](https://github.com/rendercv/rendercv/blob/main/docs/user_guide/sample_entries.yaml), which holds one sample entry per entry type. The docs build validates these samples against the standard entry types, so a sample that no longer fits its type fails the build.

## Design Images

The design gallery in the README, on the home page, and on the [Design](../user_guide/design.md) page shows the first page of each example CV. `just update-examples` regenerates them in `docs/assets/images/examples/` together with the [`examples/`](https://github.com/rendercv/rendercv/tree/main/examples) folder.

## Local Preview

```bash
just serve-docs
```

Starts a local server at `http://127.0.0.1:8000` with live reload. Edit Markdown files and see changes instantly.

```bash
just build-docs
```

Generates the final website in the `site/` directory. Mainly used by GitHub workflows for final deployment (see [GitHub Workflows](github_workflows.md)).

## Deployment

Every push to `main` triggers automatic deployment.

**The workflow** ([`.github/workflows/deploy-docs.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml)):

1. **Trigger:** Runs on every push to `main`
2. **Build step:**
      - Installs `uv` and `just`
      - Runs `just build-docs` to generate the website
      - Uploads the `site/` directory as an artifact
3. **Deploy step:**
      - Takes the uploaded artifact
      - Deploys it to GitHub Pages (a free static website hosting service)
      - Makes it available at `docs.rendercv.com`

## Learn More

See the [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/) for more information.
