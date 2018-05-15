"""A module for describing datasets and importing them."""
from typing import List

from .column import Column
from .utils import DatasetSource, get_column_name
from ..odkform.survey import SurveyRow
from ..dofile.stata_utils import clean_stata_varname, gen_anonymous_varname


class Dataset:
    """A class to describe a Dataset.

    Instance attributes:
        dataset_filename: The filename for this dataset
        dataset_source: The program that created this dataset
        begin_repeat: If this is a repeat group dataset, then this
            attribute is the survey_row that begins the repeat group
        import_context: An object to keep track of state during import
        columns: A list of Columns contained in this dataset
    """

    def __init__(self, dataset_filename: str, dataset_source: DatasetSource,
                 begin_repeat: SurveyRow = None):
        """Initialize a Dataset.

        Args:
            dataset_filename: The filename for this dataset
            dataset_source: The program that created this dataset
            begin_repeat: If this is a repeat group dataset, then this
                attribute is the survey_row that begins the repeat group
        """
        self.dataset_filename = dataset_filename
        self.dataset_source = dataset_source
        self.begin_repeat = begin_repeat
        self.import_context = ImportContext(dataset_source, begin_repeat)
        self.columns: List[Column] = []

    def add_survey_row(self, row: SurveyRow) -> None:
        """Process a SurveyRow and add to this Dataset.

        This method passes the survey row to the ImportContext to
        generate column(s)

        Args:
            row: The source survey row that becomes a dataset column
        """
        column_list = self.import_context.get_next_column(row)
        self.columns.extend(column_list)

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


class ImportContext:
    """A class to store state during the import process.

    Instance attributes:
        dataset_source: The program that created this dataset
        begin_repeat: If this is a repeat group dataset, then this
            attribute is the survey_row that begins the repeat group
        column_names: All of the column names that have been imported
        column_number: The column number for the next imported row
    """

    def __init__(self, dataset_source: DatasetSource, begin_repeat: SurveyRow):
        """Initialize this ImportContext.

        The column number is initialized to 0 for 0-indexing. It
        becomes 1 if the dataset source is ODK Briefcase to account
        for "SubmissionDate" that ODK Briefcase inserts.

        Args:
            dataset_source: The program that created this dataset
            begin_repeat: If this is a repeat group dataset, then this
                attribute is the survey_row that begins the repeat
                group
        """
        self.dataset_source = dataset_source
        self.begin_repeat = begin_repeat
        self.column_names = set()
        self.column_number = 0
        from_briefcase = self.dataset_source == DatasetSource.BRIEFCASE
        if from_briefcase and begin_repeat is None:
            # Account for "SubmissionDate" in briefcase
            self.column_number += 1

    def get_next_column(self, row: SurveyRow) -> List[Column]:
        """Get the next column based on the input SurveyRow.

        This method contains the business logic of processing the next
        survey row. It keeps track of Stata varnames, column number,
        and repeat group datasets.

        Args:
            row: The next survey row to process

        Returns:
            A list of Columns. This is a forward-thinking method.
            Future development may lead to multiple columns being
            generated (possible for GPS).
        """
        row_name = row.row_name
        ancestors = self.get_ancestors(row)
        column_name = get_column_name(row_name, ancestors, self.dataset_source)
        if row.is_begin_repeat():
            column_name = f'SET-OF-{column_name}'
        stata_cleaned = clean_stata_varname(column_name)
        stata_varname = stata_cleaned
        if stata_varname in self.column_names:
            stata_varname = gen_anonymous_varname(self.column_number)
        self.column_names.add(stata_varname)
        column = Column(self.column_number, column_name, stata_varname, row)
        self.update_column_number(column)
        return [column]

    def get_ancestors(self, row: SurveyRow) -> List[str]:
        """Get ancestors for the SurveyRow.

        For naming purposes, we need to know the ancestors of rows
        within repeats or groups. If a row is inside a begin repeat,
        then we only take ancestors after that begin repeat.

        Args:
            row: The row for which to get ancestors

        Returns:
            A list of the names of the ancestor nodes.
        """
        ancestors = list(row.ancestors)
        if self.begin_repeat is not None:
            while ancestors:
                if self.begin_repeat is ancestors.pop(0):
                    break
        return [i.row_name for i in ancestors]

    def update_column_number(self, column: Column):
        self.column_number += 1
        if column.survey_row.is_gps():
            self.column_number += 3

    def __repr__(self):
        msg = f'<dataset.ImportContext at column {self.column_number}>'
        return msg
