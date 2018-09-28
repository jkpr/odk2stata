"""A module for handling datasets derived from ODK files."""
from typing import List

from .dataset import Dataset
from .utils import DatasetSource
from ..odkform import OdkForm


class DatasetCollection:
    """A class to represent all data associated with an ODK form.

    Instance attributes:
        odkform: The source ODK form
        dataset_source: From whence the dataset originates
        primary: The primary dataset. This always exists
    """

    def __init__(self, odkform: OdkForm, dataset_source: DatasetSource):
        """Initialize a DatasetCollection.

        Right now, support multiple, but not nested repeats. Therefore,
        repeats are stored as a list.

        Args:
            odkform: The source ODK form
            dataset_source: From whence the dataset originates
        """
        self.odkform = odkform
        self.dataset_source = dataset_source
        self.primary = self.odkform_to_dataset(odkform, dataset_source)

    @staticmethod
    def odkform_to_dataset(odkform: OdkForm, dataset_source: DatasetSource) \
            -> Dataset:
        """Convert an OdkForm into a Dataset.

        Args:
            odkform: The source ODK form
            dataset_source: From whence the dataset originates

        Returns:
            A Dataset representing the primary dataset
        """
        dataset_stack = []
        primary_dataset = Dataset(odkform, dataset_source)
        current_dataset = primary_dataset
        for row in odkform.survey:
            if row.becomes_column():
                new_columns = current_dataset.add_next(row)
                if row.is_begin_repeat():
                    dataset_stack.append(current_dataset)
                    new_column = new_columns[0]
                    new_column.repeat_dataset = Dataset(odkform, dataset_source,
                                                        begin_repeat=new_column)
                    current_dataset = new_column.repeat_dataset
            elif row.is_end_repeat():
                current_dataset = dataset_stack.pop()
        return primary_dataset

    def get_repeat_datasets(self) -> List[Dataset]:
        """Return the repeat Datasets in this collection."""
        all_datasets = self.get_datasets()
        return all_datasets[:-1]

    def get_datasets(self) -> List[Dataset]:
        """Return all Datasets in this collection.

        This includes the primary dataset as the last element.

        Returns:
            A list of datasets in this collection.
        """
        return self.primary.get_datasets()

    def can_merge_single_repeat(self) -> bool:
        """Return if there a single repeat.

        We can merge a single repeat if there are exactly two datasets.
        """
        return len(self.get_datasets()) == 2

    def merged_iter(self):
        """Iterate over the columns in merged dataset order.

        Yields:
            The next Column
        """
        yield from self.primary.merged_iter()

    def ordered_iter(self):
        """Iterate over the columns as in the original ODK ordering.

        Yields:
            The next Column
        """
        yield from self.primary.ordered_iter()

    @classmethod
    def from_file(cls, path: str, dataset_source: str):
        """Initialize a DatasetCollection with a filename.

        This method is provided to initialize a DatasetCollection
        easily, possibly from the command-line or REPL.

        Args:
            path: The path where to find the ODK file
            dataset_source: From whence the dataset originates. This
                must be a string that DatasetSource understands.

        Returns:
            An initialized DatasetCollection
        """
        source = DatasetSource.from_string(dataset_source)
        odkform = OdkForm(path)
        return cls(odkform, source)

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'DatasetCollection({self.odkform!r}, "{self.dataset_source}")'
        return msg
