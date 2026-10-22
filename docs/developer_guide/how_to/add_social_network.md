# Add a New Social Network

A social network is one YAML file in [`src/rendercv/data/social_networks/`](https://github.com/rendercv/rendercv/tree/main/src/rendercv/data/social_networks). No code changes are needed.

1. Create `src/rendercv/data/social_networks/mynetwork.yaml`:

    ```yaml title="src/rendercv/data/social_networks/mynetwork.yaml"
    # MyNetwork.
    name: 'MyNetwork' # (1)!
    icon: my-icon # (2)!
    url: 'https://mynetwork.com/profile/{username}' # (3)!
    username: # (4)!
      pattern: '[a-z0-9_]+'
      hint: 'Use your username without "@", like johndoe.'
    example: 'johndoe' # (5)!
    ```

    1. What users write in `network:`.
    2. The [Font Awesome](https://fontawesome.com/search) icon shown in the header, by its name.
    3. The profile URL. `{username}` is the username. With a `username.pattern`, its named groups are available too: Mastodon's pattern `@(?P<user>[^@]+)@(?P<domain>[^@]+)` makes its URL `https://{domain}/@{user}`.
    4. Optional. Leave it out to accept any username. With `pattern`, a username must match the regular expression, and `hint` explains the format when it doesn't. Instead of `pattern`, `kind: phone` accepts a phone number and provides `{digits}` for the URL, like WhatsApp's `https://wa.me/{digits}`.
    5. A valid username. The tests check that it passes the username rules and builds a valid URL.

    Add `display: 'MyNetwork'` to show that text in the header instead of the username, like Google Scholar does with its opaque user IDs.

2. Update the JSON Schema, which lists the networks:

    ```bash
    just update-schema
    ```

3. Try it: add the network to a CV and render it to see the icon and the link.

    ```yaml
    cv:
      name: John Doe
      social_networks:
        - network: MyNetwork
          username: johndoe
    ```

4. Run the tests and update the AI agent skill:

    ```bash
    just test
    just update-skill
    ```
