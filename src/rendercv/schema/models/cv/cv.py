import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..path import ExistingPathRelativeToInput
from .custom_connection import CustomConnection
from .entry_types import MarkdownText, PhoneNumber, Url
from .section import Sections
from .social_network import SocialNetwork

# Header fields that show up as connections, in the order the user writes them.
connection_fields = (
    "location",
    "email",
    "phone",
    "website",
    "social_networks",
    "custom_connections",
)


class Cv(BaseModelWithoutExtraKeys):
    """The content of a CV: who you are, and what you did.

    Why:
        Content is independent of the design and of the entry types' looks.
        The header fields are fixed; sections hold entries of any entry type
        declared in Typst.
    """

    name: MarkdownText | None = pydantic.Field(
        default=None,
        examples=["John Doe", "Jane Smith"],
    )
    headline: MarkdownText | None = pydantic.Field(
        default=None,
        examples=["Software Engineer", "Data Scientist", "Product Manager"],
    )
    location: MarkdownText | None = pydantic.Field(
        default=None,
        examples=["New York, NY", "London, UK", "Istanbul, Türkiye"],
    )
    email: pydantic.EmailStr | list[pydantic.EmailStr] | None = pydantic.Field(
        default=None,
        description="You can provide multiple emails as a list.",
        examples=[
            "john.doe@example.com",
            ["john.doe.1@example.com", "john.doe.2@example.com"],
        ],
    )
    photo: ExistingPathRelativeToInput | pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        union_mode="left_to_right",
        description="Photo file path (relative to the YAML file) or a URL.",
        examples=["photo.jpg", "images/profile.png", "https://example.com/photo.jpg"],
    )
    phone: PhoneNumber | list[PhoneNumber] | None = pydantic.Field(
        default=None,
        description=(
            "Your phone number with country code in international format (e.g., +1 for"
            " USA, +44 for UK). You can provide multiple numbers as a list."
        ),
        examples=[
            "+1-234-567-8900",
            ["+1-234-567-8900", "+44 20 1234 5678"],
        ],
    )
    website: Url | list[Url] | None = pydantic.Field(
        default=None,
        description="You can provide multiple URLs as a list.",
        examples=[
            "https://johndoe.com",
            ["https://johndoe.com", "https://www.janesmith.dev"],
        ],
    )
    social_networks: list[SocialNetwork] | None = pydantic.Field(
        default=None,
    )
    custom_connections: list[CustomConnection] | None = pydantic.Field(
        default=None,
        description=(
            "Additional header connections you define yourself. Each item has a"
            " `placeholder` (the displayed text), an optional `url`, and the Font"
            " Awesome icon name to render (from https://fontawesome.com/search)."
        ),
        examples=[
            [
                {
                    "placeholder": "Book a call",
                    "url": "https://cal.com/johndoe",
                    "fontawesome_icon": "calendar-days",
                }
            ],
        ],
    )
    sections: Sections | None = pydantic.Field(
        default=None,
        description=(
            "The sections of your CV. Keys are section titles (e.g., Experience,"
            " Education), and values are lists of entries, or mappings of"
            " subsection titles to lists of entries. Entry types are detected from"
            " their fields."
        ),
    )
