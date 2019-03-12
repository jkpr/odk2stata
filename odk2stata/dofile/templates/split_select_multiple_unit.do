***** Begin split of "{{ orig }}"
* Create padded variable
gen {{ padded }} = " " + {{ orig }} + " "

* Build binary variables for each choice
{%- for item in gen_binaries %}
gen {{ item.binary_varname }} = 0 if {{ orig }} != ""
replace {{ item.binary_varname }} = 1 if strpos({{ padded }}, " {{ item.choice_name }} ")
label var {{ item.binary_varname }} {{ item.binary_label }}
{% endfor %}
* Clean up: reorder binary variables, label binary variables, drop padded variable
order {{ first }}-{{ last }}, after({{ orig }})
label values {{ first }}-{{ last }} {{ binary_label }}
drop {{ padded }}
