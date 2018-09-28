from typing import List

from .do_file_section import DoFileSection
from .imported_dataset import ImportedDataset, StataVar


class Destring(DoFileSection):

    DEFAULT_SETTINGS = {
        'odk_names_to_destring': [],
    }

    def __init__(self, dataset: ImportedDataset, settings: dict = None,
                 populate: bool = False):
        self.destring: List[StataVar] = []
        super().__init__(dataset, settings, populate)

    def populate(self):
        self.destring.clear()
        for var in self.dataset:
            self.analyze_variable(var)

    def analyze_variable(self, var: StataVar):
        if self.should_destring(var):
            self.destring.append(var)

    def should_destring(self, var: StataVar):
        if var.is_dropped():
            return False
        should_destring = False
        if var.is_numeric():
            should_destring = True
        elif var.get_odk_name() in self.odk_names_to_destring:
            should_destring = True
        return should_destring

    def destring_vars_iter(self):
        return (var.varname for var in self.destring)

    def do_file_iter(self):
        for column in self.destring:
            yield self.destring_do(column)

    def destring_do(self, var: StataVar) -> str:
        varname = var.varname
        destring = f'destring {varname}, replace'
        return destring

    @property
    def odk_names_to_destring(self):
        result = self.settings['odk_names_to_destring']
        return result


