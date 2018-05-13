{% import 'macros.do' as macros %}
{{ macros.section_header(4, 'Encode select ones', skipped=encode_select_one.skip) }}
{% if encode_select_one.skip is sameas false -%}
{% for do_code in encode_select_one.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
