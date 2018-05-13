{% import 'macros.do' as macros %}
{{ macros.section_header(5, 'Split select multiples', skipped=split_select_multiple.skip) }}
{% if split_select_multiple.skip is sameas false -%}
{% for do_code in split_select_multiple.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
