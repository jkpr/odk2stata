{% import 'macros.do' as macros %}
{{ macros.section_header(6, 'Label variable', skipped=label_variable.skip) }}
{% if label_variable.skip is sameas false -%}
{% for do_code in label_variable.do_file_iter() %}
{{ do_code }}
{%- endfor %}
{%- endif %}
