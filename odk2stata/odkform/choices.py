"""A module to handle everything related to ODK choices.

Module attributes:
    NumberNameChoice: A namedtuple to encapsulate the returned data for
        choice numberings.
    Choices: A class to handle all choices together. Choices can come
        from disparate source data
    ChoiceListTab: A class to represent the choices sheet, be it
        "choices" or "external_choices"
    ChoiceList: A single choice list found at a choices source data
"""
from collections import defaultdict, namedtuple
from typing import List, Dict, Tuple

import xlrd

from .components import XlsFormRow
from .components import Worksheet


NumberNameChoice = namedtuple('NumberNameChoice', ('number', 'name', 'choice'))


class ChoiceList:
    """A class to represent a single choice list.

    This class is meant to be read-only after initialization.

    Instance attributes:
        name: The name of the choice list
        choices: The list of choices
        sheet_name: The sheet name where these choices came from
        row_header: Calculated from the first row of the choices.
    """

    def __init__(self, name: str, choices: List[XlsFormRow], sheet_name: str):
        """Initialize a ChoiceList.

        Also stores the row_header for the choices as determined by
        the first choice row.

        Args:
            name: The name of the choice list
            choices: The list of choices
            sheet_name: The sheet name where these choices came from
        """
        self.name = name
        self.choices = choices
        self.sheet_name = sheet_name
        self.row_header = self.choices[0].row_header

    def are_choice_names_all_integer(self) -> bool:
        """Determine if all choice options have an integer ODK name."""
        return all(isinstance(i.row_name, int) for i in self)

    def get_choices_flexibly_numbered(self, extra_number: str = None) \
            -> List[NumberNameChoice]:
        """Get the choice list with flexible option numbers.

        Args:
            extra_number: A column where to look for a number. A number
                found here takes precedence.

        Returns:
            A list of tuples. Each tuple corresponds to a choice option
            and has the assigned choice option number, the choice name,
            and the XlsFormRow representing the choice row.
        """
        result = []
        next_number = 1
        for choice in self.choices:
            name = choice.row_name
            extra_found = choice.row_dict.get(extra_number)
            if isinstance(extra_found, int):
                value = extra_found
            elif isinstance(name, int):
                value = name
            else:
                value = next_number
            next_number = max(next_number, value) + 1
            result.append(NumberNameChoice(value, str(name), choice))
        return result

    def get_choices_strictly_numbered(self, number_column: str ='name') \
            -> List[NumberNameChoice]:
        """Get the choice list with strict option numbers.

        Args:
            number_column: A column where to look for a number.

        Returns:
            A list of tuples. Each tuple corresponds to a choice option
            and has the assigned choice option number, the choice name,
            and the XlsFormRow representing the choice row.

        Raises:
            KeyError if the supplied number_column is not in the
            header, or ValueError if not all entries are integer.
        """
        if number_column not in self.row_header:
            msg = (f'Unable to find "{number_column}" in column headers '
                   f'for choice list "{self.name}"')
            raise KeyError(msg)
        numbers = [row.row_dict[number_column] for row in self.choices]
        if any(not isinstance(i, int) for i in numbers):
            msg = (f'Choice list "{self.name}" does not define all '
                   f'options to have a number in the "{number_column}" '
                   f'column')
            raise ValueError(msg)
        result = []
        for number, choice in zip(numbers, self.choices):
            result.append(
                NumberNameChoice(number, str(choice.row_name), choice)
            )
        return result

    def __hash__(self):
        """Make a hash based on the sheet name and the list name."""
        return hash((self.sheet_name, self.name))

    def __iter__(self):
        """Return an iterator over individual choices in this list."""
        return iter(self.choices)

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<ChoiceList "{self.name}">'
        return msg


class ChoiceListTab(Worksheet):
    """A class to represent a sheet of choices or external choices.

    Instance attributes:
        header: The header for the tab
        choices: A dictionary of choice names and ChoiceLists
    """

    def __init__(self, sheet: xlrd.sheet.Sheet, datemode: int):
        """Initialize a ChoiceListTab object.

        Args:
            sheet: The xlrd sheet object for this sheet
            datemode: The xlrd datemode for the workbook
        """
        self.header: Tuple[str] = None
        self.choices: Dict[str, ChoiceList] = {}
        self.build_choices(sheet, datemode)

    def build_choices(self, sheet: xlrd.sheet.Sheet, datemode: int) -> None:
        """Parse the tab of ODK choices.

        This function modifies the instance attributes `header` and
        `choices` if there is something stored in the tab of ODK
        chocies.

        Args:
            sheet: The xlrd sheet object for this sheet
            datemode: The xlrd datemode for the workbook
        """
        _choices_dict = defaultdict(list)
        if sheet is not None:
            try:
                self.header = self.get_header(sheet, datemode)
                for i, row in enumerate(sheet.get_rows()):
                    if i == 0:
                        continue
                    row_values = [self.cell_to_value(cell, datemode) for cell in
                                  row]
                    row_dict = {k: v for k, v in zip(self.header, row_values)}
                    row_list_name = row_dict['list_name']
                    row_name = row_dict['name']
                    if row_list_name and row_name:
                        choice_row = XlsFormRow(i, row_name, self.header,
                                                row_values, row_dict)
                        _choices_dict[row_list_name].append(choice_row)
            except IndexError:
                # No header row found. Then no choices.
                pass
        for name, choices in _choices_dict.items():
            choice_list = ChoiceList(name, choices, sheet.name)
            self.choices[name] = choice_list

    def __len__(self):
        """Return the number of choice list names in this object."""
        return len(self.choices)

    def __iter__(self):
        """Return an iterator over the choice list names."""
        return iter(self.choices)

    def __getitem__(self, item):
        """Get the ChoiceList identified by the argument."""
        choice_list = self.choices.get(item)
        if choice_list is None:
            raise KeyError(item)
        return choice_list

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<ChoiceListTab with {len(self)} choice lists>'
        return msg


class Choices(Worksheet):
    """A class to handle all choices together for the OdkForm.

    This class is the container for all choices used by the OdkForm.

    Instance attributes:
        choices: A tab with choice lists
        external_choices: A tab with external choice lists
    """

    def __init__(self, workbook: xlrd.Book):
        """Initialize the choices object.

        Args:
            workbook: The xlrd book object
        """
        self.choices = self.parse_choices_from_sheet(workbook, 'choices')
        self.external_choices = \
            self.parse_choices_from_sheet(workbook, 'external_choices')

    @staticmethod
    def parse_choices_from_sheet(workbook: xlrd.Book, sheet_name: str) -> ChoiceListTab:
        """Parse choices from a choice sheet.

        Args:
            workbook: The xlrd book object
            sheet_name: The sheet name to parse as a choice sheet

        Returns:
            A ChoiceListTab representing the specified sheet
        """
        sheet = None
        try:
            sheet = workbook.sheet_by_name(sheet_name)
        except xlrd.biffh.XLRDError:
            pass
        return ChoiceListTab(sheet, workbook.datemode)

    def __repr__(self):
        """Get a representation of this object."""
        msg = (f'<Choices with {len(self.choices)} choice lists, '
               f'{len(self.external_choices)} external choice lists>')
        return msg
