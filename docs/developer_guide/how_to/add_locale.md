# Add a New Locale

A locale supplies language-specific text and date conventions, such as month names and the word for “present.” It translates RenderCV's generated labels, not the CV text the user wrote. Each locale starts from the English defaults and provides its own values.

1. Create a YAML file in `src/rendercv/schema/models/locale/other_locales/`

    ```bash
    touch src/rendercv/schema/models/locale/other_locales/mylanguage.yaml
    ```

2. Add the schema reference and provide translations

    ```yaml
    # yaml-language-server: $schema=../../../../../../schema.json
    locale:
      language: mylanguage
      last_updated: "Your translation"
      month: "Your translation"
      months: "Your translation"
      year: "Your translation"
      years: "Your translation"
      present: "Your translation"
      phrases:
        degree_with_area: "DEGREE in AREA"
      month_abbreviations:
        - Jan
        - Feb
        - Mar
        - Apr
        - May
        - Jun
        - Jul
        - Aug
        - Sep
        - Oct
        - Nov
        - Dec
      month_names:
        - January
        - February
        - March
        - April
        - May
        - June
        - July
        - August
        - September
        - October
        - November
        - December
    ```

    Translate every field, including `phrases.degree_with_area`, preserving the
    `DEGREE` and `AREA` placeholders. Check month names and abbreviations against
    [Unicode CLDR](https://github.com/unicode-org/cldr/tree/main/common/main).
    Use Gregorian **stand-alone** forms for month/year dates, following
    [CLDR's date guidance](https://cldr.unicode.org/translation/date-time/date-time-patterns),
    including lowercase letters and punctuation where appropriate. If the language
    needs more plural forms than singular/plural, use invariant duration
    abbreviations until the renderer supports those forms.

3. Add ISO 639-1 language code and flag emoji to `english_locale.py`

    Edit `src/rendercv/schema/models/locale/english_locale.py` and add your language to both mappings:

    In `language_iso_639_1`:
    ```python
    return {
        "english": "en",
        # ... existing languages
        "mylanguage": "xx",  # Add your two-letter ISO 639-1 code
    }[self.language]
    ```

    In `flag_emoji`:
    ```python
    country = {
        "english": "GB",
        # ... existing languages
        "mylanguage": "XX",  # Add your two-letter ISO 3166-1 country code
    }[self.language]
    ```

4. Update the JSON Schema

    ```bash
    just update-schema
    ```

    This regenerates `schema.json` so that editors can provide autocomplete and validation for the new locale. See [JSON Schema](../json_schema.md) for details.

5. Done. Use it:

    ```bash
    rendercv new "John Doe" --locale mylanguage
    ```
