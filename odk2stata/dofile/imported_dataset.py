from typing import Iterator, List, Optional

from .stata_utils import clean_stata_varname, gen_anonymous_varname
from ..dataset.dataset import Dataset
from ..dataset.column import Column
from ..odkform.survey import SurveyRow


class StataVar:

    def __init__(self, column: Column, varname: str):
        self.column = column
        self.orig_varname = varname
        self.varname = varname
        self.dropped = False

    def drop(self) -> None:
        self.dropped = True

    def is_dropped(self) -> bool:
        return self.dropped

    def keep(self) -> None:
        self.dropped = False

    def rename(self, varname: str) -> None:
        self.varname = varname

    def from_single_odk_row(self) -> bool:
        return self.column.from_single_odk_row()

    def based_on_odk_row(self) -> bool:
        return self.column.based_on_odk_row()

    def get_survey_row(self) -> SurveyRow:
        return self.column.get_survey_row()

    def get_odk_type(self) -> str:
        return self.column.get_odk_type()

    def get_odk_name(self) -> str:
        return self.column.get_odk_name()

    def imported_name_is_odk_name(self) -> bool:
        odk_name = self.get_odk_name()
        return odk_name == self.orig_varname

    def set_varname_to_original(self) -> None:
        self.varname = self.orig_varname

    def set_current_varname(self, varname: str) -> None:
        self.varname = varname

    def is_numeric(self) -> bool:
        return self.column.is_numeric()

    def __repr__(self):
        """Get a represenation of this object."""
        return f'StataVar({self.column!r}, {self.orig_varname!r})'


class ImportedDataset:

    def __init__(self, dataset: Dataset, case_preserve: bool,
                 merge_single_repeat: bool, merge_append: bool):
        self.case_preserve = case_preserve
        self.merge_single_repeat = merge_single_repeat
        self.merge_append = merge_append
        self.primary = dataset
        self.secondary = self.get_secondary_dataset()
        self.vars = self.import_vars()

    def get_secondary_dataset(self) -> Optional[Dataset]:
        if not self.merge_single_repeat:
            return None
        to_return = None
        for column in self.primary:
            if column.repeat_dataset:
                if to_return is None:
                    # Keep the first repeat dataset
                    to_return = column.repeat_dataset
                else:
                    # If there are more datasets, return None
                    to_return = None
                    break
        return to_return

    def import_vars(self) -> List[StataVar]:
        primary_vars = self.import_dataset(self.primary, self.case_preserve)
        secondary_vars = self.import_dataset(self.secondary, self.case_preserve)
        combined = []
        if not secondary_vars:
            combined.extend(primary_vars)
        elif not self.merge_append:
            for var in primary_vars:
                combined.append(var)
                if var.column.repeat_dataset:
                    combined.extend(secondary_vars)
        else:
            combined.extend(primary_vars)
            combined.extend(secondary_vars)
        return combined

    @staticmethod
    def import_dataset(dataset, case_preserve) -> List[StataVar]:
        stata_vars = []
        if dataset is None:
            return stata_vars
        column_names = set()
        for i, column in enumerate(dataset, start=1):
            column_name = column.column_name
            stata_cleaned = clean_stata_varname(column_name)
            if not case_preserve:
                stata_cleaned = stata_cleaned.lower()
            stata_varname = stata_cleaned
            if stata_varname in column_names:
                stata_varname = gen_anonymous_varname(i)
            column_names.add(stata_varname)
            this_stata_var = StataVar(column, stata_varname)
            stata_vars.append(this_stata_var)
        return stata_vars

    def is_merged_dataset(self):
        return self.secondary is not None

    def get_odk_source_file(self):
        """Get the ODK source file."""
        return self.primary.odkform.path

    def keep_all(self):
        """Set all variables to be un-dropped."""
        for var in self:
            var.keep()

    def set_all_varnames_to_original(self):
        for var in self:
            var.set_varname_to_original()

    def __iter__(self) -> Iterator[StataVar]:
        """Iterate over the Stata variables in this dataset."""
        return iter(self.vars)

    def __repr__(self):
        """Get a description of this object."""
        return f'<ImportedDataset, len {len(self.vars)}>'
