# The YAML Input File

The YAML input file says what your CV says. It has three top-level fields:

```yaml title="Your_Name_CV.yaml"
cv:
  ...
  # Your content (name, contact information, sections, entries)
  ...
locale:
  ...
  # Language strings (month names, "present", phrases, etc.)
  ...
settings:
  ...
  # RenderCV behavior (output paths, current date, bold keywords)
  ...
```

Only `cv` is required. The others have sensible defaults. Any file name works; `rendercv new` names it `Your_Name_CV.yaml`.

Explore the detailed documentation for each field:

- [`cv` Field](cv.md)
- [`locale` Field](locale.md)
- [`settings` Field](settings.md)

How the CV looks is not in the YAML file. That's the [design](../design.md), a Typst file named `design.typ` next to the YAML file. Which entry types the `cv` field can use is set by the [entry types](../entry_types.md), `entries.typ`. Both are optional.

!!! warning "The `design` field is gone"
    RenderCV 2 set the design in the YAML file's `design` field. A YAML file with a `design` field is an error in RenderCV 3. Run `rendercv migrate Your_Name_CV.yaml` to turn it into a `design.typ`. See [Migrating from RenderCV 2](../migrating_from_v2.md).

## JSON Schema

To maximize your productivity while editing the input YAML file, set up RenderCV's JSON Schema in your IDE. It will validate your inputs on the fly and give auto-complete suggestions for every field, including the fields of each standard entry type.

![JSON Schema in action](../../assets/images/json_schema.gif)

=== "Visual Studio Code"

    1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
    2. Name your file ending with `_CV.yaml`. The schema activates automatically.
    3. Press `Ctrl + Space` for suggestions.

=== "Other Editors"

    1. Add this line at the top of your file (`rendercv new` adds it for you):
        ```yaml
        # yaml-language-server: $schema=https://github.com/rendercv/rendercv/blob/main/schema.json?raw=true
        ```
    2. Press `Ctrl + Space` for suggestions (if your editor supports JSON Schema).

!!! note
    The JSON Schema knows only the standard entry types, so your editor may flag entries of [your own entry types](../entry_types.md#your-own-entry-types). `rendercv render` validates them against your `entries.typ`.
