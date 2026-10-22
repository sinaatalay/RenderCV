# `cv` Field

## Header Information

The `cv` field begins with your personal information. All fields are optional. RenderCV adapts to whatever you provide.

```yaml
cv:
  name: John Doe
  headline: Machine Learning Engineer
  location: San Francisco, CA
  email: john@example.com # (1)!
  phone: "+14155551234" # (2)!
  website: https://johndoe.dev # (3)!
  photo: photo.jpg # (4)!
  social_networks:
    - network: LinkedIn # (5)!
      username: johndoe
    - network: GitHub
      username: johndoe
  custom_connections:
    - placeholder: Book a call # (6)!
      url: https://cal.com/johndoe
      fontawesome_icon: calendar-days
```

1. Multiple emails can be provided as a list.
2. Write phone numbers with their country code. Multiple phone numbers can be provided as a list. How they are shown (national, international, or E.164) is a design option: [`header.connections.phone_number_format`](../design.md#options).
3. Multiple websites can be provided as a list.
4. A path relative to the YAML file, or a URL.
5. Available social networks: << available_social_networks >>. Each network checks its username format (for example, Mastodon usernames are `@username@domain`).
6. Custom connections let you add any extra link (or plain text if `url` is omitted) with your own display text (`placeholder`) and a Font Awesome icon name (e.g., `calendar-days`, `envelope`). For the list of available icons, see [fontawesome.com/search](https://fontawesome.com/search).

The header shows the connections (`location`, `email`, `phone`, `website`, `social_networks`, `custom_connections`) in the order you write them.

## Sections

The `sections` field holds the main content of your CV. It's a dictionary where:

- **Keys** are section titles (displayed as headings). Section titles can be anything.
- **Values** are lists of entries.

```yaml
cv:
  name: John Doe

  sections:
    summary:
      - Software engineer with 10 years of experience in distributed systems.

    experience:
      - company: Acme Corp
        position: Senior Engineer
        start_date: 2020-01
        end_date: present
        highlights:
          - Led migration to microservices architecture
          - Reduced deployment time by 80%

    education:
      - institution: MIT
        area: Computer Science
        degree: BS
        start_date: 2012-09
        end_date: 2016-05

    skills:
      - label: Languages
        details: Python, Go, Rust, TypeScript
      - label: Infrastructure
        details: Kubernetes, Terraform, AWS
```

Keys in `snake_case` become title case: `work_experience` is shown as "Work Experience". Keys with spaces or uppercase letters are shown as written.

**Section names are just titles.** You can use any of the << entry_type_count >> [standard entry types](../entry_types.md) in any section, or [your own](../entry_types.md#your-own-entry-types). Choose what works best for your content.

For example, an `experience` section could use `normal` entries:

```yaml
sections:
  experience:
    - name: Acme Corp — Senior Engineer
      start_date: 2020-01
      end_date: present
      highlights:
        - Led migration to microservices architecture
```

Or `bullet` entries for a minimal style:

```yaml
sections:
  experience:
    - bullet: "**Acme Corp** — Senior Engineer (2020–present)"
    - bullet: "**StartupXYZ** — Founding Engineer (2018–2020)"
```

A section can even mix entry types, though most sections look best with one.

### Subsections

To group a section's entries, write the section as a dictionary of subsection titles to lists of entries:

```yaml
sections:
  projects:
    Open source:
      - name: FlashInfer
        date: 2023
        summary: Kernels for LLM inference.
    Research:
      - name: NeuralPrune
        date: Fall 2021
```

### How RenderCV Knows an Entry's Type

You never have to say which entry type an entry is. RenderCV picks the type whose fields fit: an entry with `company` and `position` is an `experience`, an entry with `label` and `details` is a `one_line`, and an entry that is just text is a `paragraph`. See [Entry Types](../entry_types.md) for all types and their fields.

If an entry's fields fit several types (this can happen with [your own entry types](../entry_types.md#your-own-entry-types)), RenderCV asks you to choose one with the `type` key:

```yaml
sections:
  awards:
    - type: normal
      name: Best Paper Award
      date: 2021-05
```

If an entry fits no type, RenderCV tells you what's wrong with it compared to the closest type, for example: ``The entry type `experience` has no field `positon`. Did you mean `position`?``

## Text

### Markdown

All text fields support inline Markdown:

```yaml
highlights:
  - Increased revenue by **$2M** annually
  - Developed [open-source tool](https://github.com/example) with *500+ stars*
```

- `**text**` → **bold**
- `*text*` → *italic*
- `[text](url)` → hyperlink
- `` `code` `` → `code`
- `$$f(x) = x^2$$` → math, written in [Typst's math syntax](https://typst.app/docs/reference/math/)

Everything else is printed exactly as you write it. Characters like `$`, `#`, `@`, and `<` need no escaping:

```yaml
highlights:
  - "Raised $2M for C# tooling; see issue #1, or email john@doe.com"
```

!!! tip
    Quote text that contains `: ` or starts with a special character, and text with ` #` in it (YAML reads ` #` as the start of a comment). When in doubt, use double quotes.

### Typst

To write [Typst](https://typst.app/docs/reference/syntax/) markup instead of Markdown, tag the value with `!typst`:

```yaml
highlights:
  - !typst "Showed that $f(x) = x^2$ is a #emph[parabola]."
```

### Nested Bullets

In `highlights`, ` - ` inside a bullet starts nested bullets. YAML joins indented lines into one, so you can write them on their own lines:

```yaml
highlights:
  - Published research at top-tier venues
    - ICML 2022 main conference paper
    - NeurIPS 2022 workshop paper
```

This is the same as `- Published research at top-tier venues - ICML 2022 main conference paper - NeurIPS 2022 workshop paper`.

### Adding Fields

Entries only accept their entry type's fields. A field an entry type doesn't have is an error, so typos never disappear silently. To add fields (say, a `tech_stack` for jobs), [declare your own entry type](../how_to/add_fields_to_entries.md).
