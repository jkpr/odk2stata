"""Describe ODK form components that can serve as base classes.

Module attributes:
    Worksheet: A class to describe a generic worksheet
    XlsFormRow: A class to describe a row in the XlsForm
"""
import datetime
from typing import Tuple

import xlrd

from ..error import LabelNotFoundError


class Worksheet:
    """A class to represent a single tab in an XlsForm.

    The Worksheet class is a base class for other ODK form building
    blocks.

    Class attributes:
        DEFAULT_DATEMODE: the default date mode for xlrd.
    """

    DEFAULT_DATEMODE=1

    @staticmethod
    def get_header(sheet: xlrd.sheet.Sheet,
                   datemode: int = DEFAULT_DATEMODE) -> Tuple[str]:
        """Get the header row for a sheet.

        Returns:
            A tuple of str for each cell in the header row
        """
        values = Worksheet.get_row_values(sheet, 0, datemode)
        return tuple(str(val) for val in values)

    @staticmethod
    def get_row_values(sheet: xlrd.sheet.Sheet, rowx: int,
                       datemode: int = DEFAULT_DATEMODE) -> tuple:
        """Get the values from a row in a sheet.

        Returns:
            A tuple of cell values. The cell values can be any of str,
            bool, int, or float.
        """
        row = sheet.row(rowx)
        values = (Worksheet.cell_to_value(cell, datemode) for cell in row)
        return tuple(values)

    @staticmethod
    def cell_to_value(cell: xlrd.sheet.Cell, datemode: int):
        """Get the value of a single cell.

        Returns:
            If the cell is a date or an error, that is converted to
            string and returned. Otherwise, a cell can be one of str,
            bool, int, or float.
        """
        if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
            return ''
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            return cell.value.strip()
        elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return bool(cell.value)
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            int_value = int(cell.value)
            if int_value == cell.value:
                return int_value
            return cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            datetime_or_time_only = xlrd.xldate_as_tuple(cell.value, datemode)
            if datetime_or_time_only[:3] == (0, 0, 0):
                return str(datetime.time(*datetime_or_time_only[3:]))
            return str(datetime.datetime(*datetime_or_time_only))
        elif cell.ctype == xlrd.XL_CELL_ERROR:
            return f'#ERROR({cell.value})'
        else:
            return str(cell.value)


class XlsFormRow:
    """A class to represent a row in the survey or choices tab.

    XlsFormRow is a base class for other ODK form building blocks. The
    attributes here are meant to be read-only.

    Instance attributes:
        rowx: The 0-indexed row in the sheet
        row_name: The value for the name column of this row
        row_header: The headers
        row_values: The values of each cell in this row
        row_dict: An easy lookup to get the value under a header
    """

    def __init__(self, rowx: int, row_name: str, row_header: Tuple[str],
                 row_values: list, row_dict: dict):
        """Initialize an XlsFormRow.

        Args:
            rowx: The 0-indexed row in the sheet
            row_name: The value for the name column of this row
            row_header: The headers
            row_values: The values of each cell in this row
            row_dict: An easy lookup to get the value under a header
        """
        self.rowx = rowx
        self.row_name = row_name
        self.row_header = row_header
        self.row_values = row_values
        self.row_dict = row_dict

    def get_label(self, which_label: str, extra_label: str) -> str:
        """Get the label for this row.

        Args:
            which_label: Which column the label should be by default.
                This parameter can take the special value of
                "first_label" to indicate the first column that starts
                with "label".
            extra_label: A column to check first. If there is something
                there, it is used. Otherwise, the search is performed
                according to `which_label`.

        Returns:
            The label that was discovered.

        Raises:
            LabelNotFoundError: If no column is found in which to find
                a label.
        """
        result = self.row_dict.get(extra_label)
        if result:
            # We will use this label
            pass
        elif which_label == 'first_label':
            header = self.row_header
            first_label = next((i for i in header if i.startswith('label')),
                               None)
            if first_label is None:
                raise LabelNotFoundError()
            result = self.row_dict[first_label]
        elif which_label in self.row_dict:
            result = self.row_dict[which_label]
        else:
            raise LabelNotFoundError()
        str_result = str(result)
        return str_result

    def __hash__(self):
        """Make a hash based on row number and row name."""
        return hash((self.rowx, self.row_name))

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<XlsFormRow "{self.row_name}" at row {self.rowx + 1}>'
        return msg
