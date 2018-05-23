"""A module for handling datasets derived from ODK files."""
import string

from .dataset import Dataset
from .utils import DatasetSource
from ..odkform import OdkForm
from ..odkform.survey import SurveyRow


class DatasetCollection:
    """A class to represent all data associated with an ODK form.

    Instance attributes:
        odkform: The source ODK form
        dataset_source: From whence the dataset originates
        primary: The primary dataset. This always exists
        repeats: Datasets created by repeat groups. There is one for
            each repeat group
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
        primary_filename = self.dataset_filename(odkform, dataset_source)
        self.primary = Dataset(primary_filename, dataset_source)
        self.repeats = []
        datasets = [self.primary]
        for row in odkform.survey:
            if row.becomes_column():
                datasets[-1].add_survey_row(row)
            if row.is_begin_repeat():
                filename = self.dataset_filename(odkform, dataset_source,
                                                 begin_repeat=row)
                repeat_dataset = Dataset(filename, dataset_source,
                                         begin_repeat=row)
                datasets.append(repeat_dataset)
            elif row.is_end_repeat():
                self.repeats.append(datasets.pop())

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

    @staticmethod
    def dataset_filename(odkform: OdkForm, dataset_source: DatasetSource,
                         begin_repeat: SurveyRow = None) -> str:
        """Get the name of the CSV dataset.

        Args:
            odkform: The source ODK form
            dataset_source: From whence the dataset originates
            begin_repeat: If the dataset is based on a repeat group,
                this is the SurveyRow that begins the repeat group

        Returns:
            The file name, not including any path, of the dataset
        """
        form_title = odkform.settings.form_title
        filename_uncleaned = form_title
        if begin_repeat is not None:
            filename_uncleaned = f'{filename_uncleaned}_{begin_repeat.row_name}'
        if dataset_source == DatasetSource.AGGREGATE:
            filename_uncleaned = f'{filename_uncleaned}_results'
        filename = DatasetCollection.strip_illegal_chars(filename_uncleaned)
        full_filename = f'{filename}.csv'
        return full_filename

    @staticmethod
    def strip_illegal_chars(text: str) -> str:
        """Remove illegal characters.

        This routine mimics the same behavior in ODK Briefcase when it
        names the resultant dataset file (the .csv output).

        Args:
            text: Input string

        Returns:
            A string with illegal characters removed.
        """
        whitespace_dict = {ord(i): ' ' for i in string.whitespace}
        punctuation_dict = {ord(i): '_' for i in string.punctuation}
        result = text.translate({**whitespace_dict, **punctuation_dict})
        return result

    def __iter__(self):
        """Iterate over the columns of this dataset collection."""
        return DatasetIter(self)

    def __repr__(self):
        """Get a representation of this object."""
        msg = (f'DatasetCollection({repr(self.odkform)}, '
               f'"{self.dataset_source}")')
        return msg


class DatasetIter:
    """An iterator for all columns of a dataset collection.

    This iterator goes over the primary dataset. If a begin repeat is
    found, it dives into the columns of that dataset and then returns
    to the primary dataset.
    """

    def __init__(self, dataset_collection: DatasetCollection):
        """Initialize this iterator."""
        self.primary = iter(dataset_collection.primary)
        self.repeats = [iter(i) for i in dataset_collection.repeats]
        self.current = [self.primary]

    def __iter__(self):
        """Return this iterator."""
        return self

    def __next__(self):
        """Get the next column from the dataset collection."""
        try:
            col = next(self.current[-1])
            if col.survey_row.is_begin_repeat():
                self.current.append(self.repeats.pop(0))
        except StopIteration:
            self.current.pop()
            if self.current:
                col = next(self.current[-1])
            else:
                raise
        return col
