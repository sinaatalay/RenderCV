# Add a New Locale

A built-in locale is one YAML file in [`src/rendercv/data/locales/`](https://github.com/rendercv/rendercv/tree/main/src/rendercv/data/locales). The file name is the name users write in `locale.language`.

1. Create `src/rendercv/data/locales/mylanguage.yaml`, starting from [`english.yaml`](https://github.com/rendercv/rendercv/blob/main/src/rendercv/data/locales/english.yaml):

    ```yaml title="src/rendercv/data/locales/mylanguage.yaml"
    # Mylanguage locale.
    language: mylanguage
    iso_code: xx # (1)!
    direction: ltr # (2)!
    last_updated: "Your translation of 'Last updated in'"
    present: "Your translation of 'present'"
    month: "Your translation of 'month'"
    months: "Your translation of 'months'"
    year: "Your translation of 'year'"
    years: "Your translation of 'years'"
    phrases:
      degree_with_area: "#degree in #area" # (3)!
    month_abbreviations:
      - "Jan"
      - "Feb"
      - "Mar"
      - "Apr"
      - "May"
      - "June"
      - "July"
      - "Aug"
      - "Sept"
      - "Oct"
      - "Nov"
      - "Dec"
    month_names:
      - "January"
      - "February"
      - "March"
      - "April"
      - "May"
      - "June"
      - "July"
      - "August"
      - "September"
      - "October"
      - "November"
      - "December"
    ```

    1. The language's two-letter [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) code. Typst uses it for hyphenation.
    2. `ltr` (left to right) or `rtl` (right to left).
    3. Typst markup where `#degree` and `#area` are an education entry's fields. Reorder them as your language needs, like `"#area (#degree)"`.

    Every field is required, so a built-in locale never falls back to English.

2. Update the JSON Schema, which lists the built-in locales:

    ```bash
    just update-schema
    ```

    See [JSON Schema](../json_schema.md) for details.

3. Try it:

    ```bash
    rendercv new "John Doe" --locale mylanguage
    rendercv render John_Doe_CV.yaml
    ```

4. Run the tests and update the AI agent skill, which lists the locales:

    ```bash
    just test
    just update-skill
    ```
