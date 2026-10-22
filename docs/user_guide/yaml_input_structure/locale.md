# `locale` Field

The `locale` field lets you create a CV in any language by customizing month names, date formatting, and other language-specific text.

## Built-in Locales

RenderCV includes << locale_count >> languages. To use one, simply specify the language:

```yaml
locale:
  language: german
```

Available languages: << available_locales >>.

Right-to-left languages (`arabic`, `hebrew`, `persian`) set the writing direction too, so every design lays the CV out from right to left.

## Customizing a Locale

You can override any field to fine-tune the translations:

```yaml
locale:
  language: german
  present: heute  # Override just this field
```

## Phrases

`phrases` combine several fields in the language's word order. They are written in [Typst markup](https://typst.app/docs/reference/syntax/), where `#degree` and `#area` stand for the fields of an education entry:

```yaml
locale:
  language: english
  phrases:
    degree_with_area: "#area (#degree)"  # "Computer Science (PhD)" instead of "PhD in Computer Science"
```

RenderCV 2's form, `DEGREE in AREA`, is still accepted.

## Your Own Language

For a language that isn't built in, give it any name and provide all fields:

```yaml
locale:
  language: esperanto
  iso_code: eo # (1)!
  direction: ltr # (2)!
  last_updated: Laste ĝisdatigita en
  present: nun
  month: monato
  months: monatoj
  year: jaro
  years: jaroj
  phrases:
    degree_with_area: "#degree pri #area"
  month_abbreviations: [jan, feb, mar, apr, maj, jun, jul, aŭg, sep, okt, nov, dec]
  month_names:
    [januaro, februaro, marto, aprilo, majo, junio, julio, aŭgusto, septembro, oktobro, novembro, decembro]
```

1. The language's [ISO 639](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) code. Typst uses it for hyphenation, and PDF readers for accessibility.
2. `ltr` (left to right) or `rtl` (right to left).

To share it with everyone, [add it to RenderCV](../../developer_guide/how_to/add_locale.md): a built-in locale is one YAML file.

!!! tip
    To keep the locale in its own file, write it in a YAML file with a top-level `locale` field and point to it with `settings.render_command.locale` or `rendercv render --locale-catalog FILE`.
