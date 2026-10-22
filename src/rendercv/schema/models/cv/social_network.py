import dataclasses
import difflib
import functools
import pathlib
import re
from typing import Any, Self

import pydantic
import pydantic_core

from ...yaml_reader import read_yaml
from ..base import BaseModelWithoutExtraKeys
from ..custom_error_types import CustomPydanticErrorTypes
from .entry_types import validate_phone

social_networks_directory = (
    pathlib.Path(__file__).parent.parent.parent.parent / "data" / "social_networks"
)
url_placeholder_pattern = re.compile(r"\{(\w+)\}")


@dataclasses.dataclass(frozen=True, kw_only=True)
class SocialNetworkDefinition:
    """A social network RenderCV knows, read from its YAML file.

    Why:
        Each network is pure data (its URL, icon, and username rules), so each
        is one YAML file in `rendercv/data/social_networks/`. Adding a network
        is adding a file, with no code changes.
    """

    name: str
    icon: str
    url: str
    example: str
    username_kind: str | None = None
    username_pattern: str | None = None
    username_hint: str | None = None
    display: str | None = None

    def build_url(self, username: str) -> str:
        """Build a profile URL from a username.

        Why:
            URLs are URI templates: `{username}` is the username, and named
            groups of the username pattern are available too, like `{domain}`
            for Mastodon. Phone-number usernames provide `{digits}`.

        Args:
            username: A validated username.

        Returns:
            The profile URL.
        """
        values: dict[str, str] = {"username": username}
        if self.username_pattern:
            match = re.fullmatch(self.username_pattern, username)
            if match:
                values |= {
                    key: value
                    for key, value in match.groupdict().items()
                    if value is not None
                }
        if self.username_kind == "phone":
            values["digits"] = validate_phone(username).e164.removeprefix("+")
        return url_placeholder_pattern.sub(lambda m: values[m.group(1)], self.url)


@functools.cache
def get_social_network_definitions() -> dict[str, SocialNetworkDefinition]:
    """Read every social network's YAML file.

    Returns:
        Network names mapped to their definitions, sorted by name.
    """
    definitions: dict[str, SocialNetworkDefinition] = {}
    for file in sorted(social_networks_directory.glob("*.yaml")):
        data = read_yaml(file)
        username = data.get("username") or {}
        definition = SocialNetworkDefinition(
            name=str(data["name"]),
            icon=str(data["icon"]),
            url=str(data["url"]),
            example=str(data["example"]),
            username_kind=username.get("kind"),
            username_pattern=username.get("pattern"),
            username_hint=username.get("hint"),
            display=data.get("display"),
        )
        definitions[definition.name] = definition
    return dict(sorted(definitions.items(), key=lambda item: item[0].lower()))


def get_available_social_networks() -> tuple[str, ...]:
    """Return the names of the social networks RenderCV knows, sorted by name."""
    return tuple(get_social_network_definitions())


def add_social_network_names(schema: dict[str, Any]) -> None:
    """List the social networks in the JSON Schema of `network`.

    Why:
        The networks are read from their YAML files only when needed, so the
        list is added when the JSON Schema is made, not when RenderCV is
        imported.

    Args:
        schema: The JSON Schema of the `network` field.
    """
    schema["enum"] = list(get_available_social_networks())


class SocialNetwork(BaseModelWithoutExtraKeys):
    """A profile on a social network, shown in the CV's header."""

    network: str = pydantic.Field(
        json_schema_extra=add_social_network_names,
        description="The social network.",
    )
    username: str = pydantic.Field(
        description="Your username on the network.",
        examples=["johndoe", "@johndoe@mastodon.social", "12345/johndoe"],
    )

    @pydantic.field_validator("network")
    @classmethod
    def check_network(cls, network: str) -> str:
        """Check that RenderCV knows the network.

        Args:
            network: The network's name.

        Returns:
            The network's name.
        """
        if network not in get_social_network_definitions():
            suggestion = difflib.get_close_matches(
                network, list(get_available_social_networks()), n=1
            )
            hint = f" Did you mean `{suggestion[0]}`?" if suggestion else ""
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "RenderCV doesn't know the social network `{network}`.{hint} For"
                " other links, use `custom_connections`.",
                {"network": network, "hint": hint},
            )
        return network

    @pydantic.model_validator(mode="after")
    def check_username(self) -> Self:
        """Check the username against the network's rules.

        Returns:
            The social network.
        """
        definition = self.definition
        valid = True
        if definition.username_kind == "phone":
            try:
                validate_phone(self.username)
            except (pydantic.ValidationError, ValueError):
                valid = False
        elif definition.username_pattern:
            valid = re.fullmatch(definition.username_pattern, self.username) is not None
        if valid:
            # The username becomes part of the URL, which must stay valid:
            try:
                pydantic.TypeAdapter(pydantic.HttpUrl).validate_strings(self.url)
            except pydantic.ValidationError:
                valid = False
        if not valid:
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "This is not a valid {network} username. {hint}",
                {"network": definition.name, "hint": definition.username_hint or ""},
            )
        return self

    @functools.cached_property
    def definition(self) -> SocialNetworkDefinition:
        """The network's definition."""
        return get_social_network_definitions()[self.network]

    @functools.cached_property
    def url(self) -> str:
        """The profile URL."""
        return self.definition.build_url(self.username)

    @functools.cached_property
    def display_text(self) -> str:
        """What the header shows for this profile: the username, or a label."""
        return self.definition.display or self.username
