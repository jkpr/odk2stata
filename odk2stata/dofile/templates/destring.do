{% import 'macros.do' as macros -%}
{{ macros.section_header(3, 'Destring', skipped=destring.skip) }}
{% if destring.skip is sameas false -%}
{% for destring_var in destring.destring_vars_iter() %}
destring {{ destring_var }}, replace
{%- endfor %}
{%- endif %}
