label define {{ varname }}
{%- for option in options_list %} {{ option.number }} {{ option.label }}{% endfor %}
{%- if replace %}, replace{% endif %}
