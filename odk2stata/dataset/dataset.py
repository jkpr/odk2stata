from typing import List

from .column import Column
from .utils import get_column_name
from ..odkform.survey import SurveyRow
from ..dofile.stata_utils import clean_stata_varname, gen_anonymous_varname


class Dataset:

    def __init__(self, dataset_filename: str, dataset_source: str,
                 begin_repeat: SurveyRow = None):
        self.dataset_filename = dataset_filename
        self.dataset_source = dataset_source
        self.begin_repeat = begin_repeat
        self.import_context = ImportContext(dataset_source, begin_repeat)
        self.columns = []

    def add_survey_row(self, row: SurveyRow):
        column = self.import_context.get_next_column(row)
        self.columns.append(column)

    def column_iter(self):
        for column in self:
            yield column

    def __getitem__(self, item):
        return self.columns[item]

    def __len__(self):
        return len(self.columns)

    def __iter__(self):
        return iter(self.columns)

    def __repr__(self):
        msg = f'<Dataset with {len(self.columns)} columns>'
        return msg


class ImportContext:

    def __init__(self, dataset_source: str, begin_repeat: SurveyRow):
        self.dataset_source = dataset_source
        self.begin_repeat = begin_repeat
        self.column_names = set()
        self.column_number = 0
        if self.dataset_source == 'briefcase' and begin_repeat is None:
            # Account for "SubmissionDate" in briefcase
            self.column_number += 1

    def get_next_column(self, row: SurveyRow) -> Column:
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
        return column

    def get_ancestors(self, row: SurveyRow) -> List[str]:
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
