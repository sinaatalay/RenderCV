# Add a New Social Network

RenderCV turns a network name and username into a profile link. The schema checks the username and constructs the URL; the renderer adds the icon for PDF output or a network label for Markdown. Adding a network means teaching both parts about it.

1. Add network name to `SocialNetworkName` type

    Edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    type SocialNetworkName = Literal[
        "LinkedIn",
        "GitHub",
        # ... existing networks
        "MyNetwork",  # Add your network here
    ]
    ```

2. Add URL pattern to `url_dictionary`

    Edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    url_dictionary: dict[SocialNetworkName, str] = {
        "LinkedIn": "https://linkedin.com/in/",
        # ... existing networks
        "MyNetwork": "https://mynetwork.com/profile/",  # Add URL base here
    }
    ```

3. (Optional) Add username validation

    If your network has special username format requirements, edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    match network:
        case "Mastodon":
            # ... existing validations
        case "MyNetwork":
            # ... your custom validation logic
    ```

4. (Optional) Add custom URL generation

    If URL generation requires special logic (not just base + username), edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    @functools.cached_property
    def url(self) -> str:
        if self.network == "Mastodon":
            # ... existing custom logic
        elif self.network == "MyNetwork":
            # ... your custom URL generation logic
        else:
            url = url_dictionary[self.network] + self.username
        return url
    ```

5. Add Font Awesome icon

    Edit `src/rendercv/renderer/templater/connections.py`:

    ```python
    fontawesome_icons = {
        "LinkedIn": "linkedin",
        # ... existing icons
        "MyNetwork": "my-icon-name",  # Add your icon name here
    }
    ```

    The icon must exist in the icon map of the `@preview/fontawesome` version that
    `src/rendercv/renderer/rendercv_typst/lib.typ` imports, and in the Font Awesome
    fonts of `packages/rendercv-fonts`. `test_every_icon_has_a_glyph` checks both.
    See also [Font Awesome](https://fontawesome.com/search).

    Verify profile URLs and username syntax with the platform's own documentation
    or account form. Distinguish profile slugs from display names. For example,
    Itch.io uses `https://username.itch.io/`, while HuggingFace and Devpost put the
    username in the URL path. WhatsApp uses `https://wa.me/username` for usernames
    and `https://wa.me/14155552671` for international phone numbers (digits only).
    See [WhatsApp's username link documentation](https://faq.whatsapp.com/1561101675623754/)
    and [username format rules](https://faq.whatsapp.com/2535820043482794/).

6. Add test for URL generation

    Edit `tests/schema/models/cv/test_social_network.py`:

    ```python
    @pytest.mark.parametrize(
        ("network", "username", "expected_url"),
        [
            # ... existing tests
            (
                "MyNetwork",
                "myusername",
                "https://mynetwork.com/profile/myusername",
            ),
        ],
    )
    def test_url(self, network, username, expected_url):
        # test implementation
    ```

7. Add network to test fixtures

    Edit `tests/renderer/conftest.py`, add your network to the `social_networks` list:

    ```python
    social_networks=[
        SocialNetwork(network="LinkedIn", username="johndoe"),
        # ... existing networks
        SocialNetwork(network="MyNetwork", username="johndoe"),
    ]
    ```

8. Update test data and verify visual output

    ```bash
    just update-testdata
    ```

    Check the generated PDFs in `tests/renderer/testdata/test_pdf_png/` to ensure your network appears correctly with the icon.

9. Run tests to verify everything passes

    ```bash
    just test
    ```
