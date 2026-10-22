# Use the AI Agent Skill

RenderCV provides an AI agent skill that teaches AI coding assistants how to create, edit, and render CVs. Once installed, your agent gains full knowledge of RenderCV's YAML schema, entry types, CLI commands, designs, locales, and design options.

## Supported Agents

The skill works with any AI agent that supports the [skills standard](https://skills.sh), including Claude Code, Claude Desktop, Cursor, Codex, Copilot, Windsurf, and Gemini CLI.

## Install the Skill

=== "Vercel Skills CLI"

    ```bash
    npx skills add rendercv/rendercv-skill
    ```

    You can also target a specific agent:

    ```bash
    npx skills add rendercv/rendercv-skill -a claude-code
    npx skills add rendercv/rendercv-skill -a cursor
    npx skills add rendercv/rendercv-skill -a codex
    ```

=== "OpenSkills"

    ```bash
    npx openskills install rendercv/rendercv-skill
    ```

=== "Claude Desktop"

    1. Download [`rendercv_skill.zip`](../../assets/rendercv_skill.zip).
    2. In Claude Desktop, click **Customize** (top left), then select **Skills**.
    3. Click **"+"** and select **"Upload a skill"**.
    4. Upload the downloaded ZIP file.

    The skill will appear in your Skills list and Claude will automatically use it when working with your CV. See [Claude's official guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for detailed screenshots.

=== "Manual"

    Copy the content of [`skills/rendercv/SKILL.md`](https://github.com/rendercv/rendercv-skill/blob/main/skills/rendercv/SKILL.md) into your agent's skill directory. For example, for Claude Code:

    ```bash
    git clone https://github.com/rendercv/rendercv-skill.git
    cp -r rendercv-skill/skills/rendercv ~/.claude/skills/
    ```

## Auto-Generated and Evaluated

The skill is auto-generated from RenderCV's source code. A [build script](https://github.com/rendercv/rendercv/blob/main/scripts/rendercv_skill/generate.py) parses the Pydantic models via AST and strips them down to their fields, reads the standard entry types and the design options from RenderCV's Typst package, generates a sample CV, `design.typ`, and `entries.typ`, and renders everything into a single SKILL.md through a Jinja2 template. This keeps the skill always in sync with the latest RenderCV version.

We maintain a [promptfoo eval suite](https://github.com/rendercv/rendercv/tree/main/scripts/rendercv_skill/evals) that validates the skill's quality. The evals cover CV generation (software engineers, academics, fresh graduates, non-English locales), design customization, custom entry types, CLI workflows, and parsing messy CV text into clean YAML. Each generated YAML is validated through RenderCV's own validation pipeline, the same validation `rendercv render` uses, so schema violations are caught deterministically, not just with LLM-as-judge.

## What the Skill Provides

The skill gives your AI agent:

- Full knowledge of RenderCV's YAML input structure and the standard entry types
- All << design_count >> built-in designs and every design option, for `design.typ`
- How to write custom entry types in `entries.typ`
- Complete locale and language support (<< locale_count >> built-in languages)
- CLI commands and their options, including `rendercv migrate`
- Pydantic model schemas for precise field types and defaults
- A complete sample CV as a reference

## Usage

After installing the skill, simply ask your AI agent to work with your CV:

- "Create a new CV for me using the classic design"
- "Switch my CV to the engineeringresumes design"
- "Add a new experience entry to my CV"
- "Change the font to Source Sans 3 and make the margins smaller"
- "Translate my CV to German"

The agent will use its knowledge from the skill to produce correct YAML and run the right `rendercv` commands.
