"""Filling the `design.templates` of entries with the content of their fields."""

from collections.abc import Sequence
from datetime import date as Date

import pydantic

from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.section import Entry, EntryModel
from rendercv.schema.models.design.classic_theme import Templates
from rendercv.schema.models.locale.locale import Locale

from .date import compute_time_span, format_date_range, format_single_date
from .markup import (
    Break,
    Format,
    Link,
    ListMarker,
    Node,
    Text,
    bold_keywords,
    clean_url,
    emit,
    parse_content,
)
from .template import compile_template, fill_template

# Placeholders whose values are computed rather than copied from a field:
computed_placeholders = frozenset(
    {"DATE", "START_DATE", "END_DATE", "TIME_SPAN", "URL", "DOI"}
)
# Fields that are links or dates, displayed only through computed placeholders:
fields_displayed_through_placeholders = frozenset(
    {"start_date", "end_date", "doi", "url"}
)


def process_highlights(highlights: Sequence[str]) -> tuple[Node, ...]:
    """Lay out highlights as a list, with ` - ` starting a nested item.

    Why:
        YAML folds an indented sub-list (`- a\\n  - b`) into the string `a - b`, so
        ` - ` in a highlight's text starts a nested item. Only text separates
        items: ` - ` inside formatting, code, or Typst code doesn't. The lines of a
        multi-line highlight are indented, so they continue the item.

    Example:
        ```py
        emit(process_highlights(["Reduced costs - Server optimization"]), "typst")
        # Returns: "- Reduced costs\\n  - Server optimization"
        ```

    Args:
        highlights: Highlights.

    Returns:
        A list, one item per highlight.
    """
    nodes: list[Node] = []
    for highlight in highlights:
        if nodes:
            nodes.append(Break())
        nodes.append(ListMarker("- "))
        for node in parse_content(highlight):
            match node:
                case Text(text):
                    for index, item in enumerate(text.split(" - ")):
                        if index:
                            nodes.extend([Break(), ListMarker("  - ")])
                        nodes.append(Text(item))
                case Break():
                    nodes.extend([Break(), ListMarker("  ")])
                case ListMarker(source):
                    nodes.append(Text(source))
                case _:
                    nodes.append(node)
    return tuple(nodes)


def compute_entry_values(
    entry: EntryModel,
    *,
    templates: Templates,
    locale: Locale,
    show_time_span: bool,
    current_date: Date,
    output_format: Format,
) -> dict[str, tuple[Node, ...]]:
    """Compute the content of each placeholder of an entry.

    Why:
        Every scalar field (including arbitrary keys) is a placeholder named after
        it in UPPERCASE. Lists and mappings of arbitrary keys are available to Jinja
        templates but are not placeholders. `HIGHLIGHTS`, `AUTHORS`, `DATE`,
        `START_DATE`, `END_DATE`, `TIME_SPAN`, `URL`, and `DOI` are computed.

    Args:
        entry: The entry.
        templates: Templates of dates and time spans.
        locale: Locale of dates and time spans.
        show_time_span: Whether `TIME_SPAN` has a value.
        current_date: The date that "present" refers to.
        output_format: The output format.

    Returns:
        Placeholder names mapped to content.
    """
    values: dict[str, tuple[Node, ...]] = {}
    for field, value in entry.model_dump(exclude_none=True).items():
        if isinstance(value, str | int | float):
            values[field.upper()] = parse_content(str(value))

    highlights = getattr(entry, "highlights", None)
    if highlights:
        values["HIGHLIGHTS"] = process_highlights(highlights)
    authors = getattr(entry, "authors", None)
    if authors:
        values["AUTHORS"] = parse_content(", ".join(authors))

    date = getattr(entry, "date", None)
    start_date = getattr(entry, "start_date", None)
    end_date = getattr(entry, "end_date", None)
    if start_date is not None and end_date is not None:
        values["DATE"] = format_date_range(
            start_date,
            end_date,
            locale=locale,
            single_date_template=templates.single_date,
            date_range_template=templates.date_range,
            shorten=templates.shorten_date_ranges,
            output_format=output_format,
        )
        for name, value in (("START_DATE", start_date), ("END_DATE", end_date)):
            values[name] = format_single_date(
                value,
                locale=locale,
                single_date_template=templates.single_date,
                output_format=output_format,
            )
        if show_time_span:
            values["TIME_SPAN"] = compute_time_span(
                start_date,
                end_date,
                locale=locale,
                current_date=current_date,
                time_span_template=templates.time_span,
                output_format=output_format,
            )
    elif date is not None:
        values["DATE"] = format_single_date(
            date,
            locale=locale,
            single_date_template=templates.single_date,
            output_format=output_format,
        )

    if isinstance(entry, PublicationEntry) and entry.doi_url:
        values["DOI"] = values["URL"] = (Link(entry.doi_url, (Text(str(entry.doi)),)),)
    elif url := getattr(entry, "url", None):
        values["URL"] = (Link(str(url), (Text(clean_url(str(url))),)),)

    return values


def render_entry_templates(
    entry: Entry,
    *,
    templates: Templates,
    locale: Locale,
    show_time_span: bool,
    current_date: Date,
    keywords: Sequence[str],
    output_format: Format,
) -> Entry:
    """Render an entry's templates and fields in the output format.

    Why:
        Jinja templates lay out an entry from its rendered templates (e.g.
        `entry.main_column`), and custom Jinja templates can also use its rendered
        fields (e.g. `entry.company`).

    Args:
        entry: The entry. A model is modified in place.
        templates: The design's templates.
        locale: The locale.
        show_time_span: Whether `TIME_SPAN` has a value.
        current_date: The date that "present" refers to.
        keywords: Keywords to bold.
        output_format: The output format.

    Returns:
        The rendered entry: a string for a text entry, otherwise the entry itself.
    """

    def render(content: Sequence[Node]) -> str:
        return emit(bold_keywords(tuple(content), keywords), output_format)

    if isinstance(entry, str):
        return render(parse_content(entry))

    rendered: dict[str, str | list[str]] = {}
    for field, value in entry.model_dump(exclude_none=True).items():
        if field in fields_displayed_through_placeholders:
            continue
        if isinstance(value, str | int | float):
            rendered[field] = render(parse_content(str(value)))
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            rendered[field] = [render(parse_content(item)) for item in value]

    entry_templates = getattr(templates, entry.entry_type_in_snake_case, None)
    if isinstance(entry_templates, pydantic.BaseModel):
        values = compute_entry_values(
            entry,
            templates=templates,
            locale=locale,
            show_time_span=show_time_span,
            current_date=current_date,
            output_format=output_format,
        )
        names = (
            frozenset(values)
            | frozenset(field.upper() for field in type(entry).model_fields)
            | computed_placeholders
        )
        phrases = {
            name.upper(): phrase for name, phrase in locale.phrases.model_dump().items()
        }
        for template_name, source in entry_templates.model_dump(
            exclude_none=True
        ).items():
            template = compile_template(
                source, names, open_vocabulary=True, phrases=phrases
            )
            rendered[template_name] = render(
                fill_template(template, values, output_format)
            )

    for field, value in rendered.items():
        setattr(entry, field, value)
    return entry
