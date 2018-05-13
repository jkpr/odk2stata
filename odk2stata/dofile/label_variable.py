from .do_file_section import DoFileSection
from .drop_column import DropColumn
from .rename import Rename
from .stata_utils import stata_string_escape
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.column import Column


class LabelVariable(DoFileSection):

    DEFAULT_SETTINGS = {
        'first_paragraph_only': False,
        'remove_numbering': False,
        'stop_at_words': [],
        'stop_before_words': [],
    }

    def __init__(self, dataset_collection: DatasetCollection, drop_column: DropColumn,
                 rename: Rename, settings: dict = None, populate: bool = False):
        self.label_variables = []
        self.drop_column = drop_column
        self.rename = rename
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        self.label_variables.clear()
        for column in self.dataset_collection:
            self.analyze_column(column)

    def analyze_column(self, column: Column):
        if self.should_label(column):
            self.label_variables.append(column)

    def should_label(self, column: Column):
        if self.drop_column.is_dropped_column(column):
            return False
        if column.survey_row.becomes_column():
            return True
        return False

    def do_file_iter(self):
        for column in self.label_variables:
            yield self.label_variable_do(column)

    def label_variable_do(self, column: Column):
        varname = self.rename.get_varname(column.stata_varname)
        label_unquoted = column.survey_row.get_label(self.which_label,
                                                     self.extra_label)
        label_cleaned = self.clean_label(label_unquoted)
        label = stata_string_escape(label_cleaned)
        if label_cleaned == '':
            return f'* LABEL SKIPPED: variable "{varname}" has no label.'
        label_variable = f'label var {varname} {label}'
        if len(label) > 80:
            msg = (f'* LABEL TOO LONG: label is {len(label)} characters long. '
                   f'the last {len(label) - 80} characters will be lost.')
            label_variable = f'{msg}\n{label_variable}'
        return label_variable

    def clean_label(self, text: str) -> str:
        return text
