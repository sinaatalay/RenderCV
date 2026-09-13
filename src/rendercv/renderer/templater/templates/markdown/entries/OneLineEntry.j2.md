{{ entry.main_column.splitlines()[0] -}}
{% if entry.main_column.splitlines()[1:] %}


{{ entry.main_column.splitlines()[1:] | join("\n\n") }}
{%- endif %}
