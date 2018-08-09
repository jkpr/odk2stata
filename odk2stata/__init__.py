"""Generate do files for ODK using Python.

There are three primary abstractions in odk2stata. They are

    - odkform
    - dataset
    - dofile

The order is important because an XlsForm is created first as an ODK
form. That ODK form determines what the dataset looks like. The dataset
is loaded into Stata and a do file analyzes the dataset.
"""
