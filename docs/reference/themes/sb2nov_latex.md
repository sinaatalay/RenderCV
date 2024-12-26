#  `rendercv.themes.sb2nov_latex`

::: rendercv.themes.sb2nov_latex

## Jinja Templates

{% for template_name, template in theme_templates["sb2nov_latex"].items() %}
### {{ template_name }}

```latex
{{ template }}
```

{% endfor %}
