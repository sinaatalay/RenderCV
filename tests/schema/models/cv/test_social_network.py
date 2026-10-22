import json
import pathlib

import pydantic
import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.renderer.document import connection_icons
from rendercv.renderer.typst_compiler import TypstProject, query_typst
from rendercv.schema.models.cv.social_network import (
    SocialNetwork,
    SocialNetworkDefinition,
    get_available_social_networks,
    get_social_network_definitions,
    social_networks_directory,
)
from rendercv.schema.yaml_reader import read_yaml

social_network_files = sorted(social_networks_directory.glob("*.yaml"))
url_adapter = pydantic.TypeAdapter[pydantic.HttpUrl](pydantic.HttpUrl)


class TestGetSocialNetworkDefinitions:
    def test_reads_every_file(self) -> None:
        definitions = get_social_network_definitions()

        assert len(definitions) == len(social_network_files) > 0
        assert set(definitions) == {
            str(read_yaml(file)["name"]) for file in social_network_files
        }

    def test_sorts_networks_by_name(self) -> None:
        names = list(get_social_network_definitions())

        assert names == sorted(names, key=str.lower)
        assert get_available_social_networks() == tuple(names)

    @pytest.mark.parametrize("file", social_network_files, ids=lambda file: file.stem)
    def test_every_network_file_is_complete(self, file: pathlib.Path) -> None:
        data = read_yaml(file)
        definition = get_social_network_definitions()[str(data["name"])]

        assert set(data) <= {"name", "icon", "url", "username", "display", "example"}
        assert set(data.get("username") or {}) <= {"kind", "pattern", "hint"}
        assert definition.icon
        assert definition.url.startswith("https://")
        # A network with username rules explains them:
        if definition.username_pattern or definition.username_kind:
            assert definition.username_hint

    @pytest.mark.parametrize("file", social_network_files, ids=lambda file: file.stem)
    def test_every_example_builds_a_valid_url(self, file: pathlib.Path) -> None:
        name = str(read_yaml(file)["name"])
        definition = get_social_network_definitions()[name]

        social_network = SocialNetwork(network=name, username=definition.example)

        url_adapter.validate_strings(social_network.url)
        assert "{" not in social_network.url


def test_every_icon_exists_in_font_awesome(tmp_path: pathlib.Path) -> None:
    icons = sorted(
        {definition.icon for definition in get_social_network_definitions().values()}
        | set(connection_icons.values())
    )
    body = (
        '#import "@preview/fontawesome:0.6.2": fa-icon-map-common\n'
        "#let icons = (" + "".join(f"{json.dumps(icon)}, " for icon in icons) + ")\n"
        "#metadata(icons.filter(icon => icon not in"
        " fa-icon-map-common)) <missing-icons>"
    )

    assert query_typst(TypstProject(root=tmp_path), body, "missing-icons") == []


class TestSocialNetworkDefinition:
    def test_build_url_fills_in_the_username(self) -> None:
        definition = SocialNetworkDefinition(
            name="Example",
            icon="globe",
            url="https://example.com/{username}",
            example="johndoe",
        )

        assert definition.build_url("johndoe") == "https://example.com/johndoe"

    def test_build_url_fills_in_named_groups_of_the_pattern(self) -> None:
        definition = SocialNetworkDefinition(
            name="Example",
            icon="globe",
            url="https://{domain}/@{user}",
            example="@johndoe@example.com",
            username_pattern="@(?P<user>[^@]+)@(?P<domain>[^@]+)",
        )

        assert definition.build_url("@john@example.com") == "https://example.com/@john"

    def test_build_url_fills_in_the_digits_of_phone_numbers(self) -> None:
        definition = SocialNetworkDefinition(
            name="Example",
            icon="phone",
            url="https://example.com/{digits}",
            example="+14155550100",
            username_kind="phone",
        )

        assert (
            definition.build_url("+1 (415) 555-0100")
            == "https://example.com/14155550100"
        )


class TestSocialNetwork:
    @pytest.mark.parametrize(
        ("network", "username", "expected_url"),
        [
            ("LinkedIn", "myusername", "https://linkedin.com/in/myusername"),
            ("GitHub", "myusername", "https://github.com/myusername"),
            ("GitLab", "myusername", "https://gitlab.com/myusername"),
            ("IMDB", "nm0000001", "https://imdb.com/name/nm0000001"),
            ("Instagram", "myusername", "https://instagram.com/myusername"),
            ("Leetcode", "myusername", "https://leetcode.com/u/myusername"),
            ("ORCID", "0000-0000-0000-000X", "https://orcid.org/0000-0000-0000-000X"),
            ("Mastodon", "@myusername@test.org", "https://test.org/@myusername"),
            (
                "StackOverflow",
                "4567/myusername",
                "https://stackoverflow.com/users/4567/myusername",
            ),
            (
                "ResearchGate",
                "myusername",
                "https://researchgate.net/profile/myusername",
            ),
            ("YouTube", "myusername", "https://youtube.com/@myusername"),
            (
                "Google Scholar",
                "myusername",
                "https://scholar.google.com/citations?user=myusername",
            ),
            ("Telegram", "myusername", "https://t.me/myusername"),
            ("WhatsApp", "+1 415 555 0100", "https://wa.me/14155550100"),
            ("X", "myusername", "https://x.com/myusername"),
            (
                "Bluesky",
                "myusername.bsky.social",
                "https://bsky.app/profile/myusername.bsky.social",
            ),
            ("Reddit", "myusername", "https://reddit.com/user/myusername"),
        ],
    )
    def test_url(self, network: str, username: str, expected_url: str) -> None:
        assert SocialNetwork(network=network, username=username).url == expected_url

    @pytest.mark.parametrize(
        ("network", "username", "expected_display_text"),
        [
            ("GitHub", "johndoe", "johndoe"),
            ("Google Scholar", "AbCdEfGhIjK", "Google Scholar"),
        ],
    )
    def test_display_text(
        self, network: str, username: str, expected_display_text: str
    ) -> None:
        social_network = SocialNetwork(network=network, username=username)

        assert social_network.display_text == expected_display_text

    def test_definition(self) -> None:
        social_network = SocialNetwork(network="GitHub", username="johndoe")

        assert social_network.definition == get_social_network_definitions()["GitHub"]

    @pytest.mark.parametrize(
        ("network", "expected_message"),
        [
            (
                "Linkedin",
                "RenderCV doesn't know the social network `Linkedin`. Did you mean"
                " `LinkedIn`? For other links, use `custom_connections`.",
            ),
            (
                "Github",
                "RenderCV doesn't know the social network `Github`. Did you mean"
                " `GitHub`? For other links, use `custom_connections`.",
            ),
            (
                "Zzzzzz",
                "RenderCV doesn't know the social network `Zzzzzz`. For other links,"
                " use `custom_connections`.",
            ),
        ],
    )
    def test_rejects_unknown_networks_with_a_suggestion(
        self, network: str, expected_message: str
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            SocialNetwork(network=network, username="johndoe")

        error = exc_info.value.errors()[0]
        assert error["loc"] == ("network",)
        assert error["msg"] == expected_message

    @pytest.mark.parametrize(
        ("network", "username", "expected_hint"),
        [
            ("Mastodon", "invalidmastodon", 'Use the format "@username@domain".'),
            ("Mastodon", "@inva@l@id", 'Use the format "@username@domain".'),
            # Fits the pattern, but the URL's host would be invalid:
            (
                "Mastodon",
                "@invalid@ne<>twork.com",
                'Use the format "@username@domain".',
            ),
            ("StackOverflow", "invalidusername", "like 12345/johndoe."),
            ("StackOverflow", "123/invalid/username", "like 12345/johndoe."),
            ("ORCID", "0000-0000", "like 0000-0002-1825-0097."),
            ("IMDB", "0000001", "like nm0000001."),
            ("YouTube", "@johndoe", 'Leave out the "@" at the start.'),
            ("WhatsApp", "invalidphone", "with the country code"),
            ("Bluesky", "johndoe", 'without "@", like johndoe.bsky.social.'),
            ("Reddit", "invalid~username", "letters, numbers, underscores"),
            ("Reddit", "ab", "Use 3 to 23"),
        ],
    )
    def test_rejects_invalid_usernames_with_a_hint(
        self, network: str, username: str, expected_hint: str
    ) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            SocialNetwork(network=network, username=username)

        message = exc_info.value.errors()[0]["msg"]
        assert message.startswith(f"This is not a valid {network} username. ")
        assert expected_hint in message

    def test_rejects_missing_fields(self) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            SocialNetwork.model_validate({"network": "GitHub"})

        assert exc_info.value.errors()[0]["loc"] == ("username",)

    def test_json_schema_lists_the_networks(self) -> None:
        schema = SocialNetwork.model_json_schema()

        assert schema["properties"]["network"]["enum"] == list(
            get_available_social_networks()
        )

    @given(
        user=st.from_regex(r"[a-zA-Z0-9_]{1,15}", fullmatch=True),
        domain=st.from_regex(r"[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True),
    )
    def test_mastodon_url_contains_username_and_domain(
        self, user: str, domain: str
    ) -> None:
        social_network = SocialNetwork(network="Mastodon", username=f"@{user}@{domain}")

        assert social_network.url == f"https://{domain}/@{user}"

    @given(username=st.from_regex(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", fullmatch=True))
    def test_orcid_valid_format_accepted(self, username: str) -> None:
        assert SocialNetwork(network="ORCID", username=username).username == username

    @given(username=st.from_regex(r"\d{1,8}/[a-zA-Z0-9_-]+", fullmatch=True))
    def test_stackoverflow_valid_format_accepted(self, username: str) -> None:
        social_network = SocialNetwork(network="StackOverflow", username=username)

        assert social_network.url == f"https://stackoverflow.com/users/{username}"

    @given(
        network=st.sampled_from(["LinkedIn", "GitHub", "GitLab", "X", "Instagram"]),
        username=st.from_regex(r"[a-zA-Z0-9_-]{1,20}", fullmatch=True),
    )
    def test_simple_networks_build_valid_urls(
        self, network: str, username: str
    ) -> None:
        social_network = SocialNetwork(network=network, username=username)

        url_adapter.validate_strings(social_network.url)
        assert social_network.url.endswith(username)
