<div align="center">
<h1>RenderCV</h1>

_Resume builder for academics and engineers, deployed at [rendercv.com](https://rendercv.com)_

[![test](https://github.com/rendercv/rendercv/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/rendercv/rendercv/actions/workflows/test.yaml)
[![coverage](https://coverage-badge.samuelcolvin.workers.dev/rendercv/rendercv.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/rendercv/rendercv)
[![docs](<https://img.shields.io/badge/docs-mkdocs-rgb(0%2C79%2C144)>)](https://docs.rendercv.com)
[![pypi-version](<https://img.shields.io/pypi/v/rendercv?label=PyPI%20version&color=rgb(0%2C79%2C144)>)](https://pypi.python.org/pypi/rendercv)
[![pypi-downloads](<https://img.shields.io/pepy/dt/rendercv?label=PyPI%20downloads&color=rgb(0%2C%2079%2C%20144)>)](https://pypistats.org/packages/rendercv)

</div>

Write your CV or resume as YAML, then run RenderCV,

```bash
rendercv render John_Doe_CV.yaml
```

and get a PDF with perfect typography.

With RenderCV, you can:

- Version-control your CV — it's just text.
- Focus on content — don't worry about the formatting.
- Get perfect typography — consistent alignment and spacing, handled for you.

A YAML file like this:

```yaml
cv:
  name: John Doe
  location: San Francisco, CA
  email: john.doe@email.com
  website: https://rendercv.com/
  social_networks:
    - network: LinkedIn
      username: rendercv
    - network: GitHub
      username: rendercv
  sections:
    Welcome to RenderCV:
      - RenderCV reads a CV written in a YAML file, and generates a PDF with professional typography.
      - See the [documentation](https://docs.rendercv.com) for more details.
    education:
      - institution: Princeton University
        area: Computer Science
        degree: PhD
        start_date: 2018-09
        end_date: 2023-05
        location: Princeton, NJ
        highlights:
          - "Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment"
          - "Advisor: Prof. Sanjeev Arora"
          - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)
    ...
```

becomes one of these PDFs. Click on the images to preview.

| [![Classic design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/classic.png)](https://github.com/rendercv/rendercv/blob/main/examples/classic/John_Doe_CV.pdf) | [![Engineeringresumes design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/engineeringresumes.png)](https://github.com/rendercv/rendercv/blob/main/examples/engineeringresumes/John_Doe_CV.pdf) | [![Sb2nov design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/sb2nov.png)](https://github.com/rendercv/rendercv/blob/main/examples/sb2nov/John_Doe_CV.pdf) |
| --- | --- | --- |
| [![Moderncv design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/moderncv.png)](https://github.com/rendercv/rendercv/blob/main/examples/moderncv/John_Doe_CV.pdf) | [![Engineeringclassic design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/engineeringclassic.png)](https://github.com/rendercv/rendercv/blob/main/examples/engineeringclassic/John_Doe_CV.pdf) | [![Harvard design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/harvard.png)](https://github.com/rendercv/rendercv/blob/main/examples/harvard/John_Doe_CV.pdf) |
| [![Ink design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/ink.png)](https://github.com/rendercv/rendercv/blob/main/examples/ink/John_Doe_CV.pdf) | [![Opal design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/opal.png)](https://github.com/rendercv/rendercv/blob/main/examples/opal/John_Doe_CV.pdf) | [![Ember design example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/examples/ember.png)](https://github.com/rendercv/rendercv/blob/main/examples/ember/John_Doe_CV.pdf) |

## Designs in Typst

A YAML file is a complete CV. To change how it looks, put a `design.typ` next to it. Pick one of the built-in designs and change any of its options:

```typst
#import "@preview/rendercv:3.0.0": designs

#let design = designs.classic(
  page: (size: "a4", show_top_note: false),
  colors: (name: rgb("#8b0000"), section_titles: rgb("#8b0000")),
  typography: (font_family: "New Computer Modern"),
  section_titles: (type: "with_full_line"),
)
```

Switching designs is changing one word. And since it's [Typst](https://typst.app), you can go further and restyle any entry type, or write a design from scratch.

> [!TIP]
> Want a live preview while you edit? See [how to set up VS Code for RenderCV](https://docs.rendercv.com/user_guide/how_to/set_up_vs_code_for_rendercv).

## Your Own Entry Types

Education, experience, publications, skills, and more come built in. Need something else? Declare it in an `entries.typ` next to your YAML:

```typst
#import "@preview/rendercv:3.0.0": *

#let talk = entry-type(
  doc: "A talk at a conference or event.",
  fields: (
    title: field("markdown"),
    event: field("markdown"),
    date: field("date"),
  ),
  // Drawn as a normal entry, so every design styles it:
  look: (it, ctx) => as-entry("normal", name: [#it.title -- #emph(it.event)], date: it.date),
)
```

Now any entry with `title`, `event`, and `date` is a talk, validated like the built-in ones.

## JSON Schema

RenderCV's JSON Schema lets you fill out the YAML interactively, with autocompletion and inline documentation.

![JSON Schema of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/json_schema.gif)

## Strict Validation

No surprises. If something's wrong, you'll know exactly what and where, with a suggestion when it looks like a typo. If it's valid, you get a perfect PDF.

![Strict Validation Feature of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/validation.gif)

## Any Language

Pick one of the built-in languages, or fill out the locale field for your own.

```yaml
locale:
  language: english
  iso_code: en
  last_updated: Last updated in
  present: present
  month: month
  months: months
  year: year
  years: years
  phrases:
    degree_with_area: "#degree in #area"
  month_abbreviations:
    - Jan
    - Feb
    - Mar
  ...
```

## AI Agent Skill

Let AI coding agents create and edit your CV. Install the RenderCV skill:

```bash
npx skills add rendercv/rendercv-skill
```

Works with any AI agent that supports the [skills standard](https://skills.sh). The skill is [auto-generated](https://github.com/rendercv/rendercv/blob/main/scripts/rendercv_skill/generate.py) from RenderCV's source code and [evaluated](https://github.com/rendercv/rendercv/tree/main/scripts/rendercv_skill/evals) with promptfoo against RenderCV's own validation pipeline. See the [documentation](https://docs.rendercv.com/user_guide/how_to/use_the_ai_agent_skill) for details.

## JavaScript

RenderCV also runs in JavaScript, in Node.js, Bun, and browsers, with the official npm package:

```js
import { loadRenderCV } from "rendercv";

const rendercv = await loadRenderCV();
const { pdf } = await rendercv.render({ yaml });
```

See [JavaScript and Python](https://docs.rendercv.com/user_guide/javascript_and_python/) for details.

## Get Started

Install RenderCV (Requires Python 3.12+):

```
pip install "rendercv[full]"
```

Create a new CV yaml file (add `--design moderncv` to also get a `design.typ` to edit):

```
rendercv new "John Doe"
```

Edit the YAML, then render:

```
rendercv render "John_Doe_CV.yaml"
```

Coming from RenderCV 2? Run `rendercv migrate John_Doe_CV.yaml` to move your `design` field into a `design.typ`. See [migrating from RenderCV 2](https://docs.rendercv.com/user_guide/migrating_from_v2/).

For more details, see the [user guide](https://docs.rendercv.com/user_guide/).
