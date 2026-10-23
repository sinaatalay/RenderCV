from rendercv.schema.models.cv.section import BaseRenderCVSection
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import build_date_placeholders, date_object_to_string, sort_entries
from .entry_templates_from_input import render_entry_templates
from .footer_and_top_note import (
    fill_document_template,
    render_footer_template,
    render_top_note_template,
)
from .markup import Format, Node, bold_keywords, emit, parse_content, plain_text


def build_name_variants(name: str | None) -> dict[str, str]:
    """Generate all case/separator variants of a name for placeholder substitution.

    Why:
        Output file paths use placeholders like NAME_IN_LOWER_SNAKE_CASE.
        Centralizing variant generation avoids repeating the same
        null-check-and-transform pattern for each variant.

    Args:
        name: The CV owner's name, or None.

    Returns:
        Dictionary mapping placeholder names to their values, which are empty if
        there is no name.
    """
    name = name or ""
    return {
        "NAME": name,
        "NAME_IN_SNAKE_CASE": name.replace(" ", "_"),
        "NAME_IN_LOWER_SNAKE_CASE": name.replace(" ", "_").lower(),
        "NAME_IN_UPPER_SNAKE_CASE": name.replace(" ", "_").upper(),
        "NAME_IN_KEBAB_CASE": name.replace(" ", "-"),
        "NAME_IN_LOWER_KEBAB_CASE": name.replace(" ", "-").lower(),
        "NAME_IN_UPPER_KEBAB_CASE": name.replace(" ", "-").upper(),
    }


def build_document_placeholders(rendercv_model: RenderCVModel) -> dict[str, str]:
    """Build the placeholders of the document's file names, title, footer, and top note.

    Why:
        These are all about the same document, so they share one vocabulary: the
        CV owner's name (in several cases) and the current date.

    Args:
        rendercv_model: CV model.

    Returns:
        Placeholder names mapped to their values.
    """
    current_date = rendercv_model.settings._resolved_current_date
    locale = rendercv_model.locale
    return {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=rendercv_model.design.templates.single_date,
        ),
        **build_date_placeholders(current_date, locale=locale),
        **build_name_variants(rendercv_model.cv.name),
    }


def process_model(
    rendercv_model: RenderCVModel, output_format: Format
) -> RenderCVModel:
    """Render the content of a CV model in the output format, for its templates.

    Why:
        Jinja templates lay out content that is already rendered: names,
        headlines, connections, section titles, and entries are converted from
        Markdown to the output format, with keywords bolded, exactly once.

    Args:
        rendercv_model: Validated CV model. It is not modified.
        output_format: `"typst"` or `"markdown"`.

    Returns:
        A copy of the model whose content is rendered in the output format.
    """
    rendercv_model = rendercv_model.model_copy(deep=True)
    cv = rendercv_model.cv
    design = rendercv_model.design
    locale = rendercv_model.locale
    settings = rendercv_model.settings
    keywords = settings.bold_keywords
    current_date = settings._resolved_current_date
    placeholders = build_document_placeholders(rendercv_model)

    def render(content: tuple[Node, ...]) -> str:
        return emit(bold_keywords(content, keywords), output_format)

    cv._plain_name = cv.name
    if cv.name is not None:
        cv.name = render(parse_content(cv.name))
    if cv.headline is not None:
        cv.headline = render(parse_content(cv.headline))
    cv._connections = compute_connections(rendercv_model, output_format)
    cv._top_note = render(
        render_top_note_template(
            design.templates.top_note,
            placeholders=placeholders,
            last_updated=locale.last_updated,
        )
    )
    footer = render(
        render_footer_template(design.templates.footer, placeholders=placeholders)
    )
    # Page numbers are known only in the context of each page:
    cv._footer = f"context {{ [{footer}] }}" if output_format == "typst" else footer
    settings.pdf_title = plain_text(
        fill_document_template(settings.pdf_title, placeholders)
    )

    def process_section(section: BaseRenderCVSection, *, show_time_span: bool) -> None:
        section.title = render(parse_content(section.title))
        if section.entry_type == "SubsectionEntry":
            for subsection in section.entries:
                process_section(subsection, show_time_span=show_time_span)
            return
        if settings.sort_entries != "none":
            section.entries = sort_entries(
                section.entries, order=settings.sort_entries, current_date=current_date
            )
        section.entries = [
            render_entry_templates(
                entry,
                templates=design.templates,
                locale=locale,
                show_time_span=show_time_span,
                current_date=current_date,
                keywords=keywords,
                output_format=output_format,
            )
            for entry in section.entries
        ]

    for section in cv.rendercv_sections:
        section.title = locale.section_labels.get(section.key, section.title)
        # A subsection shows time spans if its section does:
        process_section(
            section,
            show_time_span=(
                section.snake_case_title in design.sections.show_time_spans_in
            ),
        )

    return rendercv_model
