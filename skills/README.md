<div align="center">
<h1>RenderCV Skill</h1>

_Give your AI agent the ability to generate professional CVs and resumes as PDF._

</div>

Install this skill and your AI agent can create, edit, and render professional CVs and resumes, just by talking to it. Describe your experience and get a polished PDF in seconds. Choose from 9 built-in themes, customize colors, fonts, margins, and more.

[RenderCV](https://github.com/rendercv/rendercv) is an open-source CV/resume builder with professional typography. This skill teaches your AI agent how to use it, so you don't have to learn anything yourself.

## Install

```bash
npx skills add rendercv/rendercv-skill
```

Works with any AI agent that supports the [skills standard](https://skills.sh), including Claude Code, Claude Desktop, Cursor, Codex, Copilot, Windsurf, Gemini CLI, and more. See the [documentation](https://docs.rendercv.com/user_guide/how_to/use_the_ai_agent_skill) for alternative install methods.

## What the Skill Provides

The skill gives your AI agent:

- Full knowledge of RenderCV's YAML input structure
- All 9 built-in themes and their design options
- Complete locale and language support (25 built-in languages)
- CLI commands and their options
- Pydantic model schemas for precise field types and defaults
- A complete sample CV as a reference

## Usage

After installing the skill, simply ask your AI agent to work with your CV:

- "Create a new CV for me using the classic theme"
- "Switch my CV to the engineeringresumes theme"
- "Add a new experience entry to my CV"
- "Change the font to Source Sans 3 and make the margins smaller"
- "Translate my CV to German"

## Auto-Generated and Evaluated

This repository is **automatically generated** from the main [rendercv/rendercv](https://github.com/rendercv/rendercv) repository. A [build script](https://github.com/rendercv/rendercv/blob/main/scripts/rendercv_skill/generate.py) parses the Pydantic models via AST, generates sample CVs and design configs, and renders everything into a single SKILL.md through a Jinja2 template, in the main repository's [`skills/`](https://github.com/rendercv/rendercv/tree/main/skills) folder, which is mirrored here. This keeps the skill always in sync with the latest RenderCV version.

A [promptfoo eval suite](https://github.com/rendercv/rendercv/tree/main/scripts/rendercv_skill/evals) validates the skill's quality. The evals cover CV generation, design customization, CLI workflows, and parsing messy CV text into clean YAML. Each generated YAML is validated through RenderCV's own Pydantic pipeline, so schema violations are caught deterministically, not just with LLM-as-judge.

**Do not open issues or pull requests here.** All contributions should go to the main repository: [rendercv/rendercv](https://github.com/rendercv/rendercv).
