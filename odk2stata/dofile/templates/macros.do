{% macro section_header(section_number, section_title, skipped=False) -%}
/* ---------------------------------------------------------
         {% if skipped %}(SKIPPED) {% endif %}SECTION {{ section_number }}: {{ section_title }}
   --------------------------------------------------------- */
{%- endmacro %}


{% macro sub_section_header(sub_section_title) -%}
/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         SUBSECTION: {{ sub_section_title }}
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
{%- endmacro %}

{% macro sub_section_footer() -%}
/* - - - END SUBSECTION  - - - - - - - - - - - - - - - - - - */
{%- endmacro %}

{% macro import_delimited(filename, case_preserve) -%}
import delimited "{{ filename }}", charset("utf-8") delimiters(",") stringcols(_all) bindquote(strict)
{%- if case_preserve %} case(preserve){% endif %} clear
{%- endmacro %}
