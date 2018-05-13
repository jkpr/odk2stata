{% import 'macros.do' as macros %}
{{ macros.section_header(3, 'Destring', skipped=destring.skip) }}
{% if destring.skip is sameas false -%}
{% for do_code in destring.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
