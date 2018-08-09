"""A module to describe the dataset based on an ODK file.

This module describes three primary abstractions:

    - DatasetCollection
    - Dataset
    - Column

An ODK file can have repeat groups. When the data are exported to CSV,
then those repeat groups become their own datasets. Therefore, the top
level is the DatasetCollection, which comprises of the primary Dataset
and repeat group Datasets. Each Dataset has Columns.
"""
from .dataset_collection import DatasetCollection


