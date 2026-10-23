---
toc_depth: 2
---

# JSON Schema

An editor can recognize valid YAML syntax without knowing what RenderCV's fields mean. It needs a description of the allowed structure to suggest field names, explain them, and flag invalid values.

[JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) is a standard format for that description. This small example describes an object with a required string field called `name`:

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Your full name"}
  },
  "required": ["name"]
}
```

An editor using it can suggest `name`, show its description, and reject a numeric value. The schema is written in JSON, but YAML editors can apply it to the corresponding data structure too.

RenderCV publishes [`schema.json`](https://github.com/rendercv/rendercv/blob/main/schema.json) for its CV files:

![JSON Schema of RenderCV](../assets/images/json_schema.gif)

## Generate the schema

The field definitions already exist in RenderCV's [Pydantic models](understanding_rendercv.md#validating-the-data). Pydantic's `model_json_schema()` converts them into JSON Schema. Generating it from those definitions avoids maintaining a second handwritten list of fields.

After changing a model, run:

```bash
just update-schema
```

This applies RenderCV's adjustments for editor use and writes `schema.json`. Commit it with the model change. Tests check that the generated file is current, built-in theme options remain constrained, and custom themes are accepted without loading Python code in the editor.

The same schema supports standalone CV, design, locale, and settings files, so its top-level fields are optional. Runtime validation still checks the combined input, local resources, custom theme options, and relationships between fields. Editor checks help while writing; they do not replace validation before rendering.

## Tell the editor which schema to use

`rendercv new` adds a comment pointing to the schema for the installed RenderCV version. For an existing file, place it at the top:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.9/schema.json

cv:
  name: John Doe
```

Keep the tag aligned with the CLI version so the editor suggests fields that installation understands. VS Code needs the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) to interpret the comment.

[SchemaStore](https://github.com/SchemaStore/schemastore) is a registry that associates filenames with schemas. Editors using it can automatically select RenderCV's schema for names ending in `_CV.yaml`. The explicit comment selects a particular version.

See [Pydantic's JSON Schema documentation](https://docs.pydantic.dev/latest/concepts/json_schema/) for the generation API.
