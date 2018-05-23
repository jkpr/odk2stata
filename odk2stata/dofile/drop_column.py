from .do_file_section import DoFileSection
from .stata_utils import is_valid_stata_varname, make_invalid_varname_comment
from ..dataset.column import Column
from ..dataset.dataset_collection import DatasetCollection


class DropColumn(DoFileSection):

    DEFAULT_SETTINGS = {
        'types_to_drop': ['note'],
        'stata_columns_to_drop': [],
        'stata_columns_not_to_drop': [],
    }

    def __init__(self, dataset_collection: DatasetCollection, settings: dict = None,
                 populate: bool = False):
        self.drop_list = []
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        self.drop_list.clear()
        for column in self.dataset_collection:
            self.analyze_column(column)

    def analyze_column(self, column: Column):
        if not column.survey_row.becomes_column():
            return
        should_drop = False
        row_type = column.survey_row.get_type()
        if self.is_drop_type(row_type):
            should_drop = True
        if self.is_dropped_name(column.stata_varname):
            should_drop = True
        if self.is_kept_name(column.stata_varname):
            should_drop = False
        if should_drop:
            self.drop_list.append(column)

    def do_file_iter(self):
        for stata_row in self.drop_list:
            varname = stata_row.stata_varname
            if not is_valid_stata_varname(varname):
                comment = make_invalid_varname_comment(varname)
                yield comment
            yield f'drop {varname}'

    def is_dropped_column(self, column: Column) -> bool:
        return column in self.drop_list

    def is_drop_type(self, row_type: str) -> bool:
        return row_type in self.types_to_drop

    def is_dropped_name(self, column_name: str) -> bool:
        return column_name in self.stata_columns_to_drop

    def is_kept_name(self, column_name: str) -> bool:
        return column_name in self.stata_columns_not_to_drop

    @property
    def types_to_drop(self):
        return self.settings['types_to_drop']

    @property
    def stata_columns_to_drop(self):
        return self.settings['stata_columns_to_drop']

    @property
    def stata_columns_not_to_drop(self):
        return self.settings['stata_columns_not_to_drop']

    def __repr__(self):
        msg = f'<DropColumn, size {len(self.drop_list)}>'
        return msg
