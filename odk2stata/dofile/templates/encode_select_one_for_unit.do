{{ foreach }} {
encode `{{ var }}', gen(`{{ var }}'{{ suffix }}) lab({{ lab }})
order `{{ var }}'{{ suffix }}, after(`{{ var }}')
drop `{{ var }}'
rename `{{ var }}'{{ suffix }} `{{ var }}'
}
