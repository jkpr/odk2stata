"""A module for describing datasets and importing them."""
from typing import List

from .column import Column
from .utils import DatasetSource, get_column_name, strip_illegal_chars
from ..odkform import OdkForm
from ..odkform.survey import SurveyRow


class Dataset:
    """A class to describe a Dataset.

    Instance attributes:
        odkform: The OdkForm from whence this dataset comes
        dataset_filename: The filename for this dataset
        dataset_source: The program that created this dataset
        begin_repeat: If this is a repeat group dataset, then this
            attribute is the Column that begins the repeat group
        import_context: An object to keep track of state during import
        columns: A list of Columns contained in this dataset
    """

    def __init__(self, odkform: OdkForm, dataset_source: DatasetSource,
                 begin_repeat: Column = None):
        """Initialize a Dataset.

        Args:
            odkform: The OdkForm from whence this dataset comes
            dataset_filename: The filename for this dataset
            dataset_source: The program that created this dataset
            begin_repeat: If this is a repeat group dataset, then this
                attribute is the Column that begins the repeat group
        """
        self.odkform = odkform
        self.dataset_source = dataset_source
        self.begin_repeat = begin_repeat
        self.dataset_filename = self.get_dataset_filename(
            self.odkform, self.dataset_source, self.begin_repeat
        )
        self.columns: List[Column] = []

        from_briefcase = self.dataset_source == DatasetSource.BRIEFCASE
        if from_briefcase and begin_repeat is None:
            self.start_with_submission_date()

    @staticmethod
    def get_dataset_filename(odkform: OdkForm, dataset_source: DatasetSource,
                             begin_repeat: Column = None) -> str:
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
            filename_uncleaned += f'_{begin_repeat.survey_row.row_name}'
        if dataset_source == DatasetSource.AGGREGATE:
            filename_uncleaned += f'_results'
        filename = strip_illegal_chars(filename_uncleaned)
        full_filename = f'{filename}.csv'
        return full_filename

    def start_with_submission_date(self):
        """Start the dataset with a column called SubmissionDate.

        Pre-condition: This should be a dataset with no columns added
        yet.
        """
        self.direct_add('SubmissionDate', None)

    def direct_add(self, column_name: str, survey_row: SurveyRow) -> Column:
        """Add a column to the dataset.

        Args:
            column_name: The name of the column in the dataset
            survey_row: The SurveyRow associated with this column

        Returns:
            The Column object created and added to the datset.
        """
        column = Column(column_name, survey_row)
        self.columns.append(column)
        return column

    def add_next(self, survey_row: SurveyRow) -> List[Column]:
        """Process a SurveyRow and add to this Dataset.

        This method passes the survey row to the ImportContext to
        generate column(s). One survey row almost always corresponds to
        one column. An exception is the geopoint type, which makes four
        columns.

        Args:
            row: The source survey row that becomes a dataset column

        Returns:
            A list of Column objects that have been added to the
            dataset.
        """
        columns = self.get_next(survey_row)
        self.columns.extend(columns)
        return columns

    def get_next(self, survey_row: SurveyRow) -> List[Column]:
        """Get the next columns based on the input SurveyRow.

        This method contains the business logic of processing the next
        survey row. It keeps track of Stata varnames, column number,
        and repeat group datasets.

        Args:
            survey_row: The next survey row to process

        Returns:
            A list of Columns associated with this survey row
        """
        columns = []
        row_name = survey_row.row_name
        ancestors = self.get_ancestors(survey_row)
        column_name = get_column_name(row_name, ancestors, self.dataset_source)
        if survey_row.is_gps():
            for suffix in 'Latitude', 'Longitude', 'Altitude', 'Accuracy':
                next_column_name = f'{column_name}-{suffix}'
                next_column = Column(next_column_name, survey_row)
                columns.append(next_column)
        elif survey_row.is_begin_repeat():
            # TODO: write a test if the repeat is inside a group.
            # TODO: is it the fully-qualified name? or just the row name?
            next_column_name = f'SET-OF-{column_name}'
            next_column = Column(next_column_name, survey_row)
            columns.append(next_column)
        else:
            next_column = Column(column_name, survey_row)
            columns.append(next_column)
        return columns

    def get_ancestors(self, survey_row: SurveyRow) -> List[str]:
        """Get ancestors for the SurveyRow.

        For naming purposes, we need to know the ancestors of rows
        within repeats or groups. If a row is inside a begin repeat,
        then we only take ancestors after that begin repeat.

        Args:
            survey_row: The row for which to get ancestors

        Returns:
            A list of the names of the ancestor nodes.
        """
        ancestors = list(survey_row.ancestors)
        if self.begin_repeat is not None:
            while ancestors:
                if self.begin_repeat.survey_row is ancestors.pop(0):
                    break
        return [i.row_name for i in ancestors]

    def get_datasets(self) -> list:
        """Return this dataset and repeat datasets under it.

        This is a depth-first search.

        Returns:
            A list of Datasets. This dataset is last in the list.
        """
        datasets = []
        for column in self:
            if column.repeat_dataset is not None:
                repeats = column.repeat_dataset.get_datasets()
                datasets.extend(repeats)
        datasets.append(self)
        return datasets

    def appended_iter(self):
        """Iterate over the columns in appended dataset order.

        This a recursive method. It descends into associated repeat
        groups as it goes along.

        1. Iterate through all columns of this dataset
        2. Along the way, keep track of the associated repeat datasets
        3. Descend and recurse in those discovered datasets

        Yields:
            The next Column
        """
        repeat_datasets = []
        for column in self:
            yield column
            if column.repeat_dataset is not None:
                repeat_datasets.append(column.repeat_dataset)
        for repeat_dataset in repeat_datasets:
            yield from repeat_dataset.appended_iter()

    def inserted_iter(self):
        """Iterate over the columns as in the original ODK ordering.

        This a recursive method. It descends into associated repeat
        groups as it goes along.

        Yields:
            The next Column.
        """
        for column in self:
            yield column
            if column.repeat_dataset is not None:
                yield from column.repeat_dataset.inserted_iter()

    def is_repeat_dataset(self) -> bool:
        """Return if this dataset is a repeat dataset."""
        return self.begin_repeat is not None

    def __getitem__(self, key):
        """Return column specified by key."""
        return self.columns[key]

    def __len__(self):
        """Return the number of columns."""
        return len(self.columns)

    def __iter__(self):
        """Return an iterator over the columns."""
        return iter(self.columns)

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<Dataset with {len(self.columns)} columns>'
        return msg
