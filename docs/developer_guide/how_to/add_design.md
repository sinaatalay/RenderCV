# Add a New Built-in Design

Built-in designs live in RenderCV's Typst package, in [`typst/designs/`](https://github.com/rendercv/rendercv/tree/main/typst/designs). Most are the classic engine with different default options, plus a few entry looks of their own (see [Understanding RenderCV](../understanding_rendercv.md#designs-are-dictionaries)).

1. Create `typst/designs/mydesign.typ`:

    ```typst title="typst/designs/mydesign.typ"
    // Mydesign: green accents, Lato, and centered section titles.

    #import "engine.typ": engine, resolve-options

    #let mydesign-defaults = (
      typography: (font_family: "Lato"),
      colors: (name: rgb(20, 90, 50), section_titles: rgb(20, 90, 50), links: rgb(20, 90, 50)),
      section_titles: (type: "centered_with_full_line"),
      entries: (highlights: (bullet: "–")),
    )

    /// The Mydesign design.
    ///
    /// - options (arguments): Options to change, e.g. `colors: (name: blue)`.
    /// -> dictionary
    #let mydesign(..options) = engine(
      resolve-options(mydesign-defaults, options.named()),
      name: "mydesign",
    )
    ```

    `mydesign-defaults` only lists the options that differ from the engine's `defaults` in [`engine.typ`](https://github.com/rendercv/rendercv/blob/main/typst/designs/engine.typ). Keep the name `<design>-defaults`, with `#let` and the closing parenthesis at the start of a line: the docs copy it from this file.

    To arrange entries differently, pass `entries: (o, parts) => (...)` to `engine`, like [`moderncv.typ`](https://github.com/rendercv/rendercv/blob/main/typst/designs/moderncv.typ) does.

2. Register it in [`typst/designs/designs.typ`](https://github.com/rendercv/rendercv/blob/main/typst/designs/designs.typ): import it, and add its name to `names`.

    ```typst
    #import "mydesign.typ": mydesign

    #let names = (
      "classic",
      // ... existing designs
      "mydesign",
    )
    ```

    RenderCV reads the built-in designs from `names`, so `rendercv new --design mydesign` works now.

3. Try it:

    ```bash
    rendercv new "John Doe" --design mydesign
    rendercv render John_Doe_CV.yaml
    ```

4. Update the generated files:

    ```bash
    just update-examples       # examples/mydesign/ and docs/assets/images/examples/mydesign.png
    just update-entry-figures  # docs/assets/images/mydesign/*.png
    just update-skill          # The AI agent skill lists the designs
    ```

5. Add it to the design gallery in `README.md` and `docs/index.md`.

6. Run the tests, and update their reference files if needed (see [Testing](../testing.md)):

    ```bash
    just test
    ```
