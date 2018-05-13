{% for comment in comments %}{{ comment }}
{% endfor -%}
encode {{ orig }}, gen({{ gen }}) lab({{ lab }})
order {{ gen }}, after({{ orig }})
drop {{ orig }}
rename {{ gen }} {{ orig }}
