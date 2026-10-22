# Add Fields to Entries

Entries only accept their entry type's fields, so a typo like `positon` is an error instead of silently disappearing. To add a field, declare an entry type that has it in `entries.typ`. This guide adds a `tech_stack` to jobs.

1. Create `entries.typ` next to your YAML file:

    ```typst title="entries.typ"
    #import "@preview/rendercv:3.0.0": *

    // A job with its tech stack: the fields of `experience`, plus `tech_stack`.
    #let job = entry-type(
      doc: "A position, with the technologies used.",
      fields: experience.fields + (
        tech_stack: field("markdown", doc: "The technologies used, like \"Python, Go\"."),
      ),
      // Drawn as an experience entry, with the tech stack as its summary:
      look: (it, ctx) => as-entry(
        "experience",
        company: it.company,
        position: it.position,
        date: it.date,
        start_date: it.start_date,
        end_date: it.end_date,
        location: it.location,
        summary: [_Tech stack:_ #it.tech_stack],
        highlights: it.highlights,
      ),
    )
    ```

    The `*` import keeps all standard entry types. `job` has every field of `experience` (`experience.fields`) plus `tech_stack`, and hands itself over to `experience`, so every design draws it like its other experience entries.

2. Use the field in the YAML:

    ```yaml
    cv:
      sections:
        experience:
          - company: Google
            position: Software Engineer
            start_date: 2020-01
            tech_stack: Python, Go, Kubernetes
            highlights:
              - Built the thing
          - company: Startup
            position: Founding Engineer
            start_date: 2018-01
            end_date: 2019-12
    ```

    An entry with `tech_stack` is a `job`; one without it is still an `experience`.

3. Render as usual:

    ```bash
    rendercv render Your_Name_CV.yaml
    ```

!!! note "Why `tech_stack` is required"
    If `tech_stack` were optional, an entry without it would fit both `experience` and `job`, and RenderCV would ask you to choose with `type:`. Making the new field required keeps every entry's type obvious. See [How an Entry Finds Its Type](../entry_types.md#how-an-entry-finds-its-type).

To show the new field somewhere else than the summary, give `job` a look of its own in your design. See [Change How an Entry Type Looks](change_how_an_entry_type_looks.md).
