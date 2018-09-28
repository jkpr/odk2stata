from typing import List

from .do_file_section import DoFileSection
from .stata_utils import is_valid_stata_varname, make_invalid_varname_comment
from .imported_dataset import ImportedDataset, StataVar


class DropColumn(DoFileSection):

    DEFAULT_SETTINGS = {
        'types_to_drop': ['note'],
        'odk_names_to_drop': [],
        'odk_names_not_to_drop': [],
    }

    def __init__(self, dataset: ImportedDataset, settings: dict = None,
                 populate: bool = True):
        self.drop: List[StataVar] = []
        super().__init__(dataset, settings, populate)

    def populate(self):
        # TODO: Do we need a drop list and to keep track in the ImportedDataset?
        self.dataset.keep_all()
        self.drop.clear()
        for var in self.dataset:
            self.analyze_variable(var)

    def analyze_variable(self, var: StataVar):
        should_drop = False
        odk_type = var.get_odk_type()
        if self.is_drop_type(odk_type):
            should_drop = True
        if self.is_dropped_odk_name(var.get_odk_name()):
            should_drop = True
        if self.is_kept_odk_name(var.get_odk_name()):
            should_drop = False
        if should_drop:
            var.drop()
            self.drop.append(var)

    def dropped_vars_iter(self):
        return (var.orig_varname for var in self.drop)

    def do_file_iter(self):
        for var in self.drop:
            varname = var.orig
            if not is_valid_stata_varname(varname):
                comment = make_invalid_varname_comment(varname)
                yield comment
            yield f'drop {varname}'

    def is_drop_type(self, row_type: str) -> bool:
        return row_type in self.types_to_drop

    def is_dropped_odk_name(self, name: str) -> bool:
        return name in self.odk_names_to_drop

    def is_kept_odk_name(self, name: str) -> bool:
        return name in self.odk_names_not_to_drop

    @property
    def types_to_drop(self):
        return self.settings['types_to_drop']

    @property
    def odk_names_to_drop(self):
        return self.settings['odk_names_to_drop']

    @property
    def odk_names_not_to_drop(self):
        return self.settings['odk_names_not_to_drop']

    def __repr__(self):
        msg = f'<DropColumn, size {len(self.drop)}>'
        return msg
