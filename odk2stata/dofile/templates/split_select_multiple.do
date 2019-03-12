{% import 'macros.do' as macros %}
{{ macros.section_header(5, 'Split select multiples', skipped=split_select_multiple.skip) }}
{% if split_select_multiple.skip is sameas false -%}
{% if ssm_details.ssm_units %}
label define {{ ssm_details.binary_define.label }} 0 {{ ssm_details.binary_define.option_label.zero }} 1 {{ ssm_details.binary_define.option_label.one }}
{% endif %}
{% for ssm_unit in ssm_details.ssm_units %}
{{ ssm_unit.render() }}
{% endfor %}
{%- endif %}
