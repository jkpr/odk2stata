{% import 'macros.do' as macros -%}
{{ macros.sub_section_header('Rename to original ODK names') }}

{% for rule in odk_name_rules -%}
rename {{ rule.old }} {{ rule.new }}
{% endfor %}
