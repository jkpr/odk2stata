{% import 'macros.do' as macros -%}
{{ macros.section_header(2, 'Rename', skipped=rename.skip) }}
{% if rename.skip is sameas false -%}

{% if rename.odk_name_rules -%}
{{ macros.sub_section_header('Rename to original ODK names') }}
{% for rule in rename.odk_name_rules -%}
rename {{ rule.old }} {{ rule.new }}
{% endfor %}
{%- endif %}

{% if rename.direct_rules -%}
{{ macros.sub_section_header('Additional renames') }}
{% for rule in rename.direct_rules %}
rename {{ rule.old }} {{ rule.new }}
{% endfor %}
{%- endif %}

{%- endif %}
