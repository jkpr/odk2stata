***** Begin split of "{{ orig }}"
* Create padded variable
gen {{ padded }} = " " + {{ orig }} + " "

* Build binary variables for each choice
{%- for varname, name, label in varname_name_labels %}
gen {{ varname }} = 0 if {{ orig }} != ""
replace {{ varname }} = 1 if strpos({{ padded }}, " {{ name }} ")
label var {{ varname }} {{ label }}
{% endfor %}
* Clean up: reorder binary variables, label binary variables, drop padded variable
order {{ first }}-{{ last }}, after({{ orig }})
label values {{ first }}-{{ last }} {{ binary_label_name }}
drop {{ padded }}
