# `rendercv.themes.classic_latex`

::: rendercv.themes.classic_latex

## Jinja Templates

{% for template_name, template in theme_templates["classic_latex"].items() %}
### {{ template_name }}

```latex
{{ template }}
```

{% endfor %}
