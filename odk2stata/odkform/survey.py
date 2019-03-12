"""Module defining survey building blocks.

Module attributes:
    SurveyRow: Subclassing XlsFormRow, this represents a row in survey
    Survey: The class to define the XlsForm survey
"""
from typing import List, Optional, Tuple

import xlrd.sheet

from .choices import ChoiceList
from .components import XlsFormRow
from .components import Worksheet
from ..error import MismatchedGroupOrRepeatError


class SurveyRow(XlsFormRow):
    """A class to represent a row in the survey tab of an XlsForm.

    This class subclasses XlsFormRow, so some attributes are
    documented there.

    This class has many convenience functions used in other subsystems
    for determining different qualities of the SurveyRow instance.

    Instance attributes:
        ancestors: The list of SurveyRow objects for the groups and
            repeats this row is nested under
        choice_list: The choice_list if this is a choice type question.
            This attribute is set after initialization by OdkForm.
    """

    def __init__(self, rowx: int, row_name: str, row_header: Tuple[str],
                 row_values: list, row_dict: dict,
                 ancestors: list):
        """Initialize a SurveyRow.

        Args:
            rowx: The 0-indexed row in the sheet
            row_name: The value for the name column of this row
            row_header: The headers
            row_values: The values of each cell in this row
            row_dict: An easy lookup to get the value under a header
            ancestors: The list of SurveyRow objects for the groups and
                repeats this row is nested under
        """
        super().__init__(rowx, row_name, row_header, row_values, row_dict)
        self.ancestors = list(ancestors)
        self.choice_list: Optional[ChoiceList] = None

    def get_type(self) -> str:
        """Return the survey row type."""
        return self.row_dict['type']

    def is_select_type(self) -> bool:
        """Return is this survey row is a select type with choices."""
        row_type = self.get_type()
        return row_type.startswith('select')

    def is_select_one(self) -> bool:
        """Return is this a (external) select one type."""
        select_one_starts = (
            'select_one ',
            'select_one_external ',
        )
        row_type = self.get_type()
        return any(row_type.startswith(item) for item in select_one_starts)

    def is_select_multiple(self) -> bool:
        """Return is this a (external) select multiple type."""
        select_multiple_starts = (
            'select_multiple ',
            'select_multiple_external ',
        )
        row_type = self.get_type()
        return any(row_type.startswith(item) for item in select_multiple_starts)

    def is_select_external(self) -> bool:
        """Return is this a select external (single or multiple) type."""
        external_starts = (
            'select_one_external ',
            'select_multiple_external ',
        )
        row_type = self.get_type()
        return any(row_type.startswith(item) for item in external_starts)

    def get_select_list_name(self):
        """Get the list name of the associated choice list."""
        if self.is_select_type():
            row_type = self.get_type()
            _, choice_list = row_type.rsplit(maxsplit=1)
            return choice_list
        return None

    def is_begin_repeat(self):
        """Return is this a begin repeat type."""
        row_type = self.get_type()
        is_begin_repeat = row_type == 'begin repeat'
        return is_begin_repeat

    def is_end_repeat(self):
        """Return is this an end repeat type."""
        row_type = self.get_type()
        is_end_repeat = row_type == 'end repeat'
        return is_end_repeat

    def is_gps(self):
        """Return is this a geopoint type."""
        row_type = self.get_type()
        is_gps = row_type in ('hidden geopoint', 'geopoint')
        return is_gps

    def is_numeric_type(self):
        """Return is this a numeric type."""
        row_type = self.get_type()
        is_numeric = row_type in (
            'hidden decimal',
            'decimal',
            'hidden integer',
            'integer',
            'int',
            'range',
        )
        return is_numeric

    def becomes_column(self):
        """Return if this survey row becomes a column in the dataset."""
        row_type = self.get_type()
        # Note: "begin repeat" does become a column
        non_columns = ('begin group', 'end group', 'end repeat')
        return row_type not in non_columns

    def becomes_single_column(self):
        """Return if this survey row becomes a single column."""
        return self.becomes_column() and not self.is_gps()

    def __hash__(self):
        """Make a hash based on the row number and the row name."""
        return hash((self.rowx, self.row_name))

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<SurveyRow "{self.row_name}" at row {self.rowx}>'
        return msg


class Survey(Worksheet):
    """A class to represent survey in XlsForm.

    Instance attributes:
        header: The header row for the survey tab
        rows: The survey rows in the survey tab
    """

    def __init__(self, sheet: xlrd.sheet.Sheet, datemode: int):
        """Initialize a Survey.

        Args:
            sheet: The xlrd sheet that stores the survey
            datemode: The datemode for the workbook
        """
        self.header: Tuple[str] = self.get_header(sheet, datemode)
        self.rows: List[SurveyRow] = []
        self._parse_survey(sheet, datemode)

    def _parse_survey(self, sheet: xlrd.sheet.Sheet, datemode: int) -> None:
        """Parse the survey tab.

        This method goes through each row in the survey tab. If a row
        has a type and a name, then a SurveyRow is created for it.
        Nesting under groups and repeats is accounted for.

        Args:
            sheet: The xlrd sheet that stores the survey
            datemode: The datemode for the workbook
        """
        ancestors = []
        for i, row in enumerate(sheet.get_rows()):
            if i == 0:
                continue
            row_values = [self.cell_to_value(cell, datemode) for cell in row]
            row_dict = {k: v for k, v in zip(self.header, row_values)}
            row_type = row_dict['type']
            row_name = row_dict['name']
            if row_type in ('end group', 'end repeat'):
                if not ancestors:
                    msg = (f'Found "{row_type}" without matching "begin ..." '
                           f'at row {i+1}')
                    raise MismatchedGroupOrRepeatError(msg)
                ancestors.pop()
            if row_type and row_name:
                survey_row = SurveyRow(i, row_name, self.header, row_values,
                                       row_dict, ancestors)
                self.rows.append(survey_row)
                if row_type in ('begin group', 'begin repeat'):
                    ancestors.append(survey_row)
        if ancestors:
            first_ancestor = ancestors[-1]
            msg = (f'No "end ..." at end of XlsForm to match "begin ..." with '
                   f'name "{first_ancestor}"')
            raise MismatchedGroupOrRepeatError(msg)

    def __getitem__(self, item) -> SurveyRow:
        """Get the survey row specified by the argument."""
        return self.rows[item]

    def __iter__(self):
        """Return an iterator over survey rows."""
        return iter(self.rows)

    def __len__(self):
        """Return the length of survey as the number of survey rows."""
        return len(self.rows)

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<Survey {len(self.rows)} rows, {len(self.header)} columns>'
        return msg
