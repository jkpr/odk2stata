# Installation

To install `odk2stata` for the first time, run:

```
python3 -m pip install https://github.com/jkpr/odk2stata/zipball/master
```

### Upgrade

If you already have `odk2stata` installed, then run:

```
python3 -m pip install https://github.com/jkpr/odk2stata/zipball/master --upgrade
```

# Generate a Stata do file from an XlsForm

The do file does various useful things, including:

- Import the dataset with all string variables
- Drop columns, notes by default
- Rename columns
- Destring numeric types
- Encode `select_one` variables with the name or the label
- Split `select_multiple` variables
- Label the column variables, using the label by default


