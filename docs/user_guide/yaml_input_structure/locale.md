# `locale` Field

The `locale` field lets you create a CV in any language by customizing month names, date formatting, and other language-specific text.

## Built-in Locales

RenderCV includes translations for << locale_count >> languages. To use one, simply specify the language:

```yaml
locale:
  language: german
```

Available languages: << available_locales >>.

## Section Titles

Use `section_labels` to translate headings while keeping the same section keys
in each language:

```yaml
cv:
  sections:
    experience:
      - company: Acme
        position: Engineer
locale:
  language: italian
  section_labels:
    experience: Esperienza lavorativa
```

Labels match the exact keys under `cv.sections`. Keys without a label keep their
usual titles. Overlays, command-line overrides, and design options such as
`show_time_spans_in: [experience]` still use the original key. Subsection titles
are text in the CV itself and are not looked up in this mapping. Built-in locales
leave this mapping empty because section keys and titles are yours to choose.

## Customizing Locale

You can override any field to fine-tune the translations:

```yaml
locale:
  language: german
  present: jetzt  # Override just this field
```

Or create a completely custom locale:

```yaml
locale:
  language: english
  last_updated: Last updated in
  month: month
  months: months
  year: year
  years: years
  present: present
  month_abbreviations:
    - Jan
    - Feb
    - Mar
    - Apr
    - May
    - June
    - July
    - Aug
    - Sept
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
