* Give the merge column a unique id where it is missing: _n is the row number
replace {{ key }} = string(_n) if {{ key }} == ""
merge 1:m {{ key }} using {{ using_dataset }}
* Remove the row numbers that were added in
replace {{ key }} = "" if length({{ key }}) < 13
