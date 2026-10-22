import dataclasses
import pathlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from rendercv.schema.models.cv.entry_types import (
    Bullet,
    DateValue,
    Entry,
    EntryTypeDeclaration,
    FieldDeclaration,
)
from rendercv.schema.models.cv.section import Section
from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import substitute_date_and_name_placeholders
from .rich_text import markdown_to_rich_text, rich_text_to_plain_text

# The version of the data format RenderCV sends to the Typst package.
data_format_version = 1

connection_icons = {
    "location": "location-dot",
    "email": "envelope",
    "phone": "phone",
    "website": "link",
}


def clean_url(url: str) -> str:
    """Shorten a URL for display: no scheme, no "www.", no trailing slash.

    Example:
        ```py
        clean_url("https://www.example.com/")  # "example.com"
        ```

    Args:
        url: The URL.

    Returns:
        The shortened URL.
    """
    return re.sub(r"^(https?://)?(www\.)?", "", str(url)).rstrip("/")


def encode_date(value: DateValue) -> dict[str, Any]:
    """Encode a date the way the Typst package reads it.

    Args:
        value: The date.

    Returns:
        `{year, month, day}`, `{present: true}`, or `{text: rich text}`.
    """
    if value.present:
        return {"present": True}
    if value.text is not None:
        return {"text": markdown_to_rich_text(value.text)}
    return {
        key: getattr(value, key)
        for key in ("year", "month", "day")
        if getattr(value, key) is not None
    }


def encode_bullet(bullet: Bullet) -> dict[str, Any]:
    """Encode a bullet and its nested bullets."""
    return {
        "body": markdown_to_rich_text(bullet.body),
        "children": [encode_bullet(child) for child in bullet.children],
    }


def encode_value(
    value: Any,
    field: FieldDeclaration,
    entry_types: Mapping[str, EntryTypeDeclaration],
) -> Any:
    """Encode a validated field value the way the Typst package reads it.

    Args:
        value: The validated value.
        field: The field's declaration.
        entry_types: All entry types, for nested entries.

    Returns:
        The value as JSON-compatible data.
    """
    if value is None:
        return None
    match field.kind:
        case "markdown":
            return markdown_to_rich_text(value)
        case "date":
            return encode_date(value)
        case "phone":
            return dataclasses.asdict(value)
        case "bullets":
            return [encode_bullet(bullet) for bullet in value]
        case "list":
            item_field = dataclasses.replace(
                field, kind=field.of or "markdown", of=None
            )
            return [encode_value(item, item_field, entry_types) for item in value]
        case "entries":
            return [encode_entry(entry, entry_types) for entry in value]
        case _:
            return value


def encode_entry(
    entry: Entry, entry_types: Mapping[str, EntryTypeDeclaration]
) -> dict[str, Any]:
    """Encode an entry: its type's name and its field values.

    Args:
        entry: The validated entry.
        entry_types: All entry types.

    Returns:
        `{type, fields}`.
    """
    fields = entry_types[entry.type_name].fields
    return {
        "type": entry.type_name,
        "fields": {
            name: encode_value(value, fields[name], entry_types)
            for name, value in entry.values.items()
            if value is not None
        },
    }


def encode_section(
    section: Section, entry_types: Mapping[str, EntryTypeDeclaration]
) -> dict[str, Any]:
    """Encode a section with its entries and subsections."""
    return {
        "key": section.key,
        "title": markdown_to_rich_text(section.title),
        "entries": [encode_entry(entry, entry_types) for entry in section.entries],
        "subsections": [
            encode_section(subsection, entry_types)
            for subsection in section.subsections
        ],
    }


def as_list(value: Any) -> list[Any]:
    """Return a field that may hold one value or a list as a list."""
    if value is None:
        return []
    if isinstance(value, list | tuple):
        return list(value)
    return [value]


def text_connection(kind: str, text: str, url: str | None) -> dict[str, Any]:
    """Encode a connection shown as plain text."""
    return {
        "kind": kind,
        "icon": connection_icons[kind],
        "url": url,
        "text": [text],
        # Email addresses and phone numbers are shown as they are, not as URLs:
        "url_text": (
            clean_url(url) if url and not url.startswith(("mailto:", "tel:")) else text
        ),
    }


def encode_connections(
    model: RenderCVModel, order: Sequence[str]
) -> list[dict[str, Any]]:
    """Encode the header's connections in the order the user wrote them.

    Args:
        model: The validated CV.
        order: The `cv` keys in the order they appear in the YAML.

    Returns:
        The connections: `{kind, icon, url, text, url_text}`, plus `phone` for
        phone numbers and `network` for social networks.
    """
    cv = model.cv
    connections: list[dict[str, Any]] = []
    for key in order:
        if key == "location" and cv.location is not None:
            connections.append(
                {
                    "kind": "location",
                    "icon": connection_icons["location"],
                    "url": None,
                    "text": markdown_to_rich_text(cv.location),
                }
            )
        elif key == "email":
            connections.extend(
                text_connection("email", str(email), f"mailto:{email}")
                for email in as_list(cv.email)
            )
        elif key == "phone":
            for phone in as_list(cv.phone):
                connection = text_connection("phone", phone.national, phone.uri)
                connection["phone"] = dataclasses.asdict(phone)
                connections.append(connection)
        elif key == "website":
            connections.extend(
                text_connection("website", clean_url(website), website)
                for website in as_list(cv.website)
            )
        elif key == "social_networks":
            connections.extend(
                {
                    "kind": "social",
                    "network": social_network.network,
                    "icon": social_network.definition.icon,
                    "url": social_network.url,
                    "text": [social_network.display_text],
                    "url_text": clean_url(social_network.url),
                }
                for social_network in cv.social_networks or []
            )
        elif key == "custom_connections":
            connections.extend(
                {
                    "kind": "custom",
                    "icon": custom_connection.fontawesome_icon,
                    "url": str(custom_connection.url)
                    if custom_connection.url
                    else None,
                    "text": markdown_to_rich_text(custom_connection.placeholder),
                    "url_text": (
                        clean_url(str(custom_connection.url))
                        if custom_connection.url
                        else custom_connection.placeholder
                    ),
                }
                for custom_connection in cv.custom_connections or []
            )
    return connections


def build_document_data(
    model: RenderCVModel,
    entry_types: Mapping[str, EntryTypeDeclaration],
    *,
    connection_order: Sequence[str],
    photo: str | None = None,
) -> dict[str, Any]:
    """Build the data the Typst package renders a CV from.

    Why:
        This is the contract between RenderCV's Python and Typst sides: the
        CV's content, fully validated and resolved, as plain data. Typst never
        receives generated code, only this.

    Args:
        model: The validated CV.
        entry_types: The entry types the CV was validated against.
        connection_order: The `cv` keys in the order they appear in the YAML.
        photo: The photo's path relative to the Typst root, starting with "/".

    Returns:
        The data, ready to be sent to Typst as JSON.
    """
    current_date = model.settings.resolved_current_date
    name = model.cv.name
    return {
        "version": data_format_version,
        "settings": {
            "current_date": {
                "year": current_date.year,
                "month": current_date.month,
                "day": current_date.day,
            },
            "bold_keywords": list(model.settings.bold_keywords),
            "pdf_title": substitute_date_and_name_placeholders(
                model.settings.pdf_title, model
            ),
        },
        "locale": model.locale.model_dump(),
        "header": {
            "name": markdown_to_rich_text(name) if name else None,
            "plain_name": rich_text_to_plain_text(markdown_to_rich_text(name))
            if name
            else None,
            "headline": markdown_to_rich_text(model.cv.headline)
            if model.cv.headline
            else None,
            "photo": photo,
            "connections": encode_connections(model, connection_order),
        },
        "sections": [
            encode_section(section, entry_types) for section in model.cv.sections or []
        ],
    }


def photo_import_path(photo: pathlib.Path, root: pathlib.Path) -> str:
    """Write the photo's path the way the main Typst file reads it.

    Args:
        photo: The photo's absolute path.
        root: The Typst root.

    Returns:
        The path relative to the root, starting with "/".
    """
    return "/" + photo.relative_to(root).as_posix()
