---
toc_depth: 2
---

# Documentation

[Zensical](https://zensical.org/docs/) is a **static site generator**: it reads the Markdown pages in `docs/` and builds HTML, stylesheets, and JavaScript for a browser. Contributors edit text files; Zensical supplies navigation, search, and the visual theme. GitHub Pages serves the generated files at [docs.rendercv.com](https://docs.rendercv.com), so it does not need to run Python for each visitor.

## Preview and build

```bash
just serve-docs
just build-docs
```

`just serve-docs` starts a local preview at `http://localhost:8000` and updates it as files change. `just build-docs` writes the complete site to `site/`. It runs in strict mode, where warnings fail the build, so broken documentation is caught before deployment.

## Configuration and appearance

[`zensical.toml`](https://github.com/rendercv/rendercv/blob/main/zensical.toml) defines the navigation, extensions, metadata, and Zensical's modern theme. Add new pages to its `project.nav` list.

An **override** replaces one of the theme's templates with our own file. Overrides give us control but must be maintained when Zensical changes, so keep them small. Brand colors and the logo animation live in `docs/assets/`; custom icons live in `docs/overrides/.icons/`. Header, navigation tabs, and logo rendering use Zensical's own templates.

The remaining `toc-item.html` override limits the table of contents using `toc_depth`. This setting appears in **front matter**, the YAML block between `---` lines at the top of a page. A value of `2` includes headings down to level two.

When changing an override, compare it with the matching template in [Zensical UI](https://github.com/zensical/ui). Zensical uses MiniJinja for theme templates; use its supported filters and tests rather than Python methods. Follow the [customization guide](https://zensical.org/docs/customization/), and check desktop and mobile navigation, search, and both color schemes after a theme upgrade.

## Generated content

The **macros extension** lets a page insert Python values or call functions while it is built. The native `zensical.extensions.macros` extension loads [`docs/docs_templating.py`](https://github.com/rendercv/rendercv/blob/main/docs/docs_templating.py), which supplies model defaults and examples directly from RenderCV. For example, the theme list comes from the code's theme registry, so adding a theme updates that list automatically. Custom delimiters distinguish these insertions from ordinary Jinja examples. A failure fails the build.

The [API Reference](../api_reference/index.md) describes Python functions and classes. Its text comes from **docstrings**, the descriptions written inside their definitions. The native `zensical.extensions.mkdocstrings` extension and its Python handler render them; Zensical's built-in `api-autonav` support creates the module pages and navigation. Edit the source docstrings to update these descriptions.

The [entry figures](../user_guide/yaml_input_structure/cv.md) come from `docs/user_guide/sample_entries.yaml`. Run `just update-entry-figures` to render them directly to PNG with Typst. Each preview uses an automatically sized page, so no PDF cropping or image conversion tools are needed.

## Deployment

The [documentation workflow](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml) runs on pushes to `main` and manual dispatch. It builds the site, uploads `site/` as an artifact, and deploys that artifact to GitHub Pages.
