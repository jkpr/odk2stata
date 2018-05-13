{% import 'macros.do' as macros %}
{{ macros.section_header(2, 'Rename', skipped=rename.skip) }}
{% if rename.skip is sameas false -%}
{% for do_code in rename.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
