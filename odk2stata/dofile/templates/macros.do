{% macro section_header(section_number, section_title, skipped=False) -%}
/* --------------------------------------------------------
        {% if skipped %}(SKIPPED) {% endif %}SECTION {{ section_number }}: {{ section_title }}
   -------------------------------------------------------- */
{%- endmacro %}
