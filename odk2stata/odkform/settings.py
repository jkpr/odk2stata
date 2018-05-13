"""A module to define the Settings class."""
import os.path

import xlrd.sheet

from .components import Worksheet


class Settings(Worksheet):
    """A class to represent the settings of an XlsForm.

    Instance attributes:
        path: The path to where the XlsForm is stored
        settings: A dictionary of settings properties and values
    """

    def __init__(self, path: str, sheet: xlrd.sheet.Sheet,
                 datemode: int = Worksheet.DEFAULT_DATEMODE):
        """Initialize the Settings object.

        If settings does not define form_title or form_id, they are
        computed using the path to the XlsForm file.

        Args:
            path: The path to where the XlsForm is stored
            sheet: The xlrd sheet that stores the settings
            datemode: The datemode for the workbook
        """
        self.path = path
        self.settings = {}
        if sheet is not None:
            self._parse_settings(sheet, datemode)
        self.settings['form_title'] = self.form_title
        self.settings['form_id'] = self.form_id

    @property
    def form_title(self):
        """Get the settings form_title."""
        form_title = self.settings.get('form_title')
        if not form_title:
            _, full_filename = os.path.split(self.path)
            filename, _ = os.path.splitext(full_filename)
            form_title = filename
        return form_title

    @property
    def form_id(self):
        """Get the settings form_id."""
        form_id = self.settings.get('form_id')
        if not form_id:
            form_id = self.form_title
        return form_id

    def _parse_settings(self, sheet: xlrd.sheet.Sheet, datemode: int):
        """Get settings.

        Pre-condition: sheet is not None.

        Args:
            sheet: The xlrd sheet that stores the settings
            datemode: The datemode for the workbook
        """
        try:
            keys = self.get_header(sheet, datemode)
            values = self.get_row_values(sheet, 1, datemode)
            self.settings = {k: v for k, v in zip(keys, values)}
        except IndexError:
            pass

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<Settings {repr(self.settings)}>'
        return msg
