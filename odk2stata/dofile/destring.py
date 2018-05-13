from .do_file_section import DoFileSection
from .drop_column import DropColumn
from .rename import Rename
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.column import Column


class Destring(DoFileSection):

    DEFAULT_SETTINGS = {
        'stata_columns_to_destring': [],
    }

    def __init__(self, dataset_collection: DatasetCollection,
                 drop_column: DropColumn,
                 rename: Rename, settings: dict = None, populate: bool = False):
        self.destring = []
        self.drop_column = drop_column
        self.rename = rename
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        self.destring.clear()
        for column in self.dataset_collection:
            self.analyze_column(column)

    def analyze_column(self, column: Column):
        if self.should_destring(column):
            self.destring.append(column)

    def should_destring(self, column: Column):
        if self.drop_column.is_dropped_column(column):
            return False
        should_destring = False
        if column.survey_row.is_numeric_type():
            should_destring = True
        elif column.stata_varname in self.stata_columns_to_destring:
            should_destring = True
        return should_destring

    def do_file_iter(self):
        for column in self.destring:
            yield self.destring_do(column)

    def destring_do(self, column: Column) -> str:
        varname = self.rename.get_varname(column.stata_varname)
        destring = f'destring {varname}, replace'
        return destring

    @property
    def stata_columns_to_destring(self):
        result = self.settings['stata_columns_to_destring']
        return result


