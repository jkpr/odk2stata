Configuration
=============

A primary goal of ``odk2stata`` is to be configurable, while using sensible defaults out of the box.

The configuration file can be created using::

  $ python3 -m odk2stata.dofile.settings

and for version 0.2.5, the settings file looks like

.. literalinclude:: includes/settings_v0_2_5.ini

An .ini file is broken into sections, demarcated by ``[section_heading]``.
The ``odk2stata`` .ini settings file roughly has one section per area of work. Those
sections are described below.

.. note:: The .ini file is parsed using Python's ``configparser`` module. Therefore, the settings in ``[DEFAULT]`` are applied to all other sections as default key-value pairs.

.. note:: ``odk2stata`` uses single strings and lists as values in the .ini file. Lists are made by putting one entry per line. The second line and after need to be indented so that the parser does not confuse them as keys.

Section: ``DEFAULT``
--------------------

skip = False
  Should a section be skipped? Default is ``False``, not to skip.

omit = False
  Should a section be omitted? Default is ``False``, not to omit.

dataset_source = briefcase
  Where does a dataset come from? Options are ``briefcase``, ``aggregate``, and ``no_groups``

which_label = first_label
  Which label in ``survey`` or ``choices`` should be used? This value can be the exact name of a column to specify that one, or the special term ``first_label`` to mean the first label column on a sheet.

extra_label = o2s_label
  Which column should be used as a label override? Default is ``o2s_label``, meaning that a new column should be added to the xlsform with a header ``o2s_label``. If a value is found in this column, it is used preferentially over the column for ``which_label``.

Section: ``destring``
---------------------

This section handles the destringing portion of odk2stata.
Since output datafiles are CSV, all values are treated as strings on import and then destringed. ``odk2stata`` knows to destring columns based off of integer and decimal types.

odk_names_to_destring = 
  A list of names of additional columns to destring.

Section: ``drop_column``
------------------------

types_to_drop = note
  ODK types to drop automatically. Default is ``note``. ODK datasets include columns for notes, so notes are dropped automatically.

odk_names_to_drop = 
  A list of ODK names (survey tab) to drop. Default is empty list.

odk_names_not_to_drop = 
  A list of ODK names not to drop. Default is empty list.

Section: ``encode_select_one``
------------------------------


encode_select_ones = True
  Should ``select_one`` question types be encoded at all? Default is ``True``.

encode_external_select_ones = False
  Should external ``select_one`` question types be encoded at all? Default is ``False``.

odk_names_to_encode = 
  A list of additional ODK names to encode.

odk_names_not_to_encode = 
  A list of ODK names not to encode.

choice_lists_not_to_encode = 
  A list of list names on the ``choices`` tab that should not be encoded.

number_column = o2s_number
  The column in the ``choices`` tab where the numbers to be used can be found. Default is ``o2s_number``.

strict_numbering = False
  Strict numbering means that if there are some choices without numbers in ``number_column``, the program should error out.
  Default is ``False``. If numbers are missing in the ``number_column`` then they are filled in starting with 1.

label_replace_column = first_label
  Encoding labels should be replaced with entries in this column. Default is ``first_label`` or the first column with a label.

Section: ``label_variable``
---------------------------

first_paragraph_only = False
  Use the first paragraph only when labeling a variable.

remove_numbering = True
  Remove question numbering at the beginning.

stop_at_words = 
  Use the label up to and including any of the words in this list.

stop_before_words = 
  Use the label up to but not including any of the words in this list.

Section: ``metadata``
---------------------

author = 
  Who is the author of this Stata do file?

timestamp_format = %Y-%m-%d, %H:%M:%S
  What is the timestamp format for dates and times?

case_preserve = False
  Should case be preserved on the first Stata infile? Default is ``False`` so that case is not preserved.

merge_single_repeat = True
  If there is a single repeat group, should it be merged into the dataset?
  If there are multiple repeat groups, then each repeat group has its own do file section, since they generate their own datasets.

merge_append = True
  If merging takes place should the do file append the variables to the end? If so, set this to ``True``.
  False inserts the variables where they occur in the XLSForm.

odk2stata_version = 0.2.5
  What is the version of ``odk2stata``? Default is generated from within the code.

Section: ``rename``
-------------------
direct_rename = 
  A list of direct renames. An example is ``var1 myVariable``.

rename_to_odk_name = True
  Should Stata variables be renamed to their ODK name? Default is ``True`` to do such renaming.

Section: ``split_select_multiple``
----------------------------------

default_split_method = append_number
  How should the new variables be named?
  Default is ``append_number`` to take the original variable and append a number.
  Other options are ``append_name`` to take the originl variable and append the choice name and ``name_only`` to use the choice name only as the new variable.

binary_option_label = yes_no
  What should the binary variables be labeled as? Default is ``yes_no`` for "Yes" and "No".

binary_label = o2s_binary_label
  What should the Stata label name be in the do file? Default is ``o2s_binary_label``.

choices_to_exclude = negative_numbers
  Which choices to exclude? Setting this to ``negative_numbers`` means that any choice name that is a negative number does not get a new variable.

choice_lists_to_split = 
  Which choice lists should be split? This is a list.

choice_lists_not_to_split = 
  Which choice lists should not be split? This is a list.

odk_names_to_split = 
  Which ODK names should be split? This is a list.

odk_names_not_to_split = 
  Which ODK names should not be split? This is a list.

odk_names_to_append_name = 
  Which ODK names should be split in the ``append_name`` style?

odk_names_to_append_number = 
  Which ODK names should be split in the ``append_number`` style?

odk_names_to_name_only = 
  Which ODK names should be split in the ``name_only`` style?

number_column = o2s_number
  What column should be used to look for choice numbers? Default is ``o2s_number``.

strict_numbering = False
  Strict numbering means that if there are some choices without numbers in ``number_column``, the program should error out.
  Default is ``False``. If numbers are missing in the ``number_column`` then they are filled in starting with 1.

