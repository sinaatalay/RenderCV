# Custom Fonts

RenderCV comes with these fonts: << available_font_families >>. Fonts installed on your computer work too. For any other font, put its files in a `fonts` folder next to your YAML input file.

## How to Use Custom Fonts

1. Create a `fonts` directory in the same location as your YAML file:

    ```
    Your_Name_CV.yaml
    design.typ
    fonts/
      CustomFont-Regular.ttf
      CustomFont-Bold.ttf
      AnotherFont.otf
    ```

2. In your `design.typ`, set the font family:

    ```typst title="design.typ"
    #import "@preview/rendercv:3.0.0": designs

    #let design = designs.classic(
      typography: (font_family: "CustomFont"),
    )
    ```

    To use different fonts for different parts, give a dictionary instead:

    ```typst
    typography: (
      font_family: (
        body: "CustomFont",
        name: "AnotherFont",
        headline: "CustomFont",
        connections: "CustomFont",
        section_titles: "AnotherFont",
      ),
    ),
    ```

See [Design](../design.md) for all options.

## Supported Font Formats

- `.ttf` (TrueType Font)
- `.otf` (OpenType Font)

## Font Family Names

Use the font family name exactly as defined in the font file's metadata. For most fonts, this is the name you see when you install the font on your system.
