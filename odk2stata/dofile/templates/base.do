{% import 'macros.do' as macros -%}
/*
 *  Generated using odk2stata.py, version {{ metadata.odk2stata_version }}
 *
 *  ODK Source: {{ metadata.odk_source_file }}
 *  Primary CSV dataset: {{ metadata.primary_csv }}
{%- if metadata.is_merged_dataset() %}
 *  Secondary CSV dataset: {{ metadata.secondary_csv }}
{%- endif %}
 *  Date: {{ metadata.date_created }}
 *  Author: {{ metadata.author }}
 */

{% if metadata.is_merged_dataset() -%}
{{ macros.import_delimited(metadata.secondary_csv, metadata.case_preserve) }}
save "{{ metadata.secondary_dta }}", replace

{% endif -%}

{{ macros.import_delimited(metadata.primary_csv, metadata.case_preserve) }}

{%- if metadata.is_merged_dataset() %}

* Give the merge column a unique id where it is missing: _n is the row number
replace {{ metadata.get_merge_key() }} = string(_n) if {{ metadata.get_merge_key() }} == ""
merge 1:m {{ metadata.get_merge_key() }} using "{{ metadata.secondary_dta }}"
* Remove the row numbers that were added in
replace {{ metadata.get_merge_key() }} = "" if length({{ metadata.get_merge_key() }}) < 13
{%- endif %}

{% include "cleaning.do" %}

local today=c(current_date)
local date=subinstr("`today'", " ", "", .)
save "{{ metadata.primary_base }}_`date'.dta", replace
