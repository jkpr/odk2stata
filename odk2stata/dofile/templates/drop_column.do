{% import 'macros.do' as macros %}
{{ macros.section_header(1, 'Drop columns', skipped=drop_column.skip) }}
{% if drop_column.skip is sameas false -%}
{% for do_code in drop_column.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
