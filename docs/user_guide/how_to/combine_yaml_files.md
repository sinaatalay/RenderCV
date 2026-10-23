# Combine YAML Files

A CV doesn't have to be one file. RenderCV can read it from several files, which is useful to:

- reuse a design or a locale in several CVs,
- keep a part of a CV, like publications, in its own file,
- publish a CV without its private data (your phone number or address), and render it with that data on your computer.

## Design, locale, and settings files

The `design`, `locale`, and `settings` fields can each be in their own file, which then has that field at the top:

```yaml
# design.yaml
design:
  theme: moderncv
  page:
    size: a4
```

Refer to them in the CV:

```yaml
cv:
  name: John Doe
settings:
  render_command:
    design: design.yaml
    locale: locale.yaml
```

or on the command line: `rendercv render CV.yaml --design design.yaml --locale-catalog locale.yaml --settings settings.yaml`. Such a file **replaces** its field in the CV.

## Overlays

An overlay is a YAML file **merged over** the CV. It has the structure of a CV file, with only the fields it changes: its mappings are merged into the CV's, and its other values (text and lists) replace the CV's.

### Keep private data out of a public CV

Publish the CV with placeholders:

```yaml
# CV.yaml
cv:
  name: John Doe
  email: john@example.com
  phone: "+1-555-555-5555"
```

and keep the real values in a file that you don't publish (add it to `.gitignore`):

```yaml
# private.yaml
cv:
  email: john.doe@mail.com
  phone: "+1-415-555-2671"
```

Render with the real values:

```bash
rendercv render CV.yaml --overlay private.yaml
```

### Keep a part of a CV in its own file

```yaml
# publications.yaml
cv:
  sections:
    publications:
      - title: My Paper
        authors:
          - John Doe
        date: 2024-01
```

List it in the CV, so that it's merged in every render:

```yaml
# CV.yaml
cv:
  name: John Doe
  sections:
    experience:
      - ...
    publications: [] # The overlay's publications go here.
settings:
  render_command:
    overlays:
      - publications.yaml
```

A section that only an overlay has is added after the CV's sections, so an empty section keeps its place.

### Replace a list

Lists are replaced as a whole, including sections, highlights, authors, and
subsection entries. An overlay does not append items or match them by position.
For example, if the CV contains `highlights: [Research, Teaching]`, an overlay
with `highlights: [Engineering]` produces `[Engineering]`. Use `[]` to clear a
list. Applying the same overlay twice gives the same result.

To keep some entries and remove or reorder others for a particular job, put the
complete desired list in the overlay. This also means that changing one subsection
through an overlay requires providing its section's complete list. A command-line
override such as `--cv.sections.experience.0.company Acme` can change one field
by position instead.

## Precedence

Each layer takes precedence over the previous ones:

1. The CV file.
2. The design, locale, and settings files, which replace their fields.
3. The overlays listed in `settings.render_command.overlays`, then the ones given with `--overlay`, merged in order.
4. Single values given on the command line, like `--cv.phone "+1-415-555-2671"`.

Errors are reported in the file that a value comes from, and `--watch` re-renders when any of the files changes.
