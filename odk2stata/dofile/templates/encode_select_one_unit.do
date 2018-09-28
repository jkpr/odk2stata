encode {{ orig }}, gen({{ gen }}) lab({{ lab }})
order {{ gen }}, after({{ orig }})
drop {{ orig }}
rename {{ gen }} {{ orig }}
