Welcome to odk2stata's documentation!
=====================================

The Python 3 package ``odk2stata`` is a configurable Stata do file generator.
The only inputs to this software are the source XLSForm and, optionally, a configuration file.

This package generates a Stata do file to complete several routine data cleansing tasks. They are:

1. Import a dataset. Merge in a single repeat group.
2. Drop columns. By default, all notes are dropped.
3. Rename columns. By default, columns are renamed back to the original ODK name.
4. Destring numeric columns.
5. Encode ``select_one`` variables. This turns the column data from ODK choice names to numbers with those names as labels.
6. Split ``select_multiple`` variables so that each choice option is a binary variable (selected or not).
7. Label column variables. The label is used as the default.

This documentation explains how to use ``odk2stata`` and how to configure it.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   configuration



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
