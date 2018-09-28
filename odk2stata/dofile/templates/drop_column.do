{% import 'macros.do' as macros -%}
{{ macros.section_header(1, 'Drop columns', skipped=drop_column.skip) }}
{% if drop_column.skip is sameas false -%}
{% for dropped_var in drop_column.dropped_vars_iter() %}
drop {{ dropped_var }}
{%- endfor %}
{%- endif %}
