"""Module defining OdkForm."""
import xlrd

from .choices import Choices
from .settings import Settings
from .survey import Survey
from ..error import OdkFormError


class OdkForm:
    """Define the OdkForm class.

    Instance attributes:
        path: The path to where the XlsForm is stored
        survey: The survey component
        choices: The choices component
        settings: The settings component
    """

    def __init__(self, path: str):
        """Initialize an OdkForm.

        The survey, choices, and settings are initialized separately.
        Lastly, the survey rows are associated with their choice lists.

        Args:
            path: The path to where the XlsForm is stored
        """
        self.path = path
        workbook = xlrd.open_workbook(self.path)
        self.survey = self._parse_survey(workbook)
        self.choices = self._parse_choices(workbook)
        self.settings = self._parse_settings(self.path, workbook)
        self._associate_choice_lists()

    @staticmethod
    def _parse_survey(workbook: xlrd.Book) -> Survey:
        """Parse the survey for the ODK form.

        Args:
            workbook: The xlrd book object

        Returns:
            A Survey object
        """
        try:
            sheet = workbook.sheet_by_name('survey')
            return Survey(sheet, workbook.datemode)
        except xlrd.biffh.XLRDError:
            msg = 'XlsForm file does not have required "survey" tab!'
            raise OdkFormError(msg)

    @staticmethod
    def _parse_choices(workbook: xlrd.Book) -> Choices:
        """Parse the choices for the ODK form.

        Args:
            workbook: The xlrd book object

        Returns:
            A Choices object
        """
        return Choices(workbook)

    @staticmethod
    def _parse_settings(path: str, workbook: xlrd.Book) -> Settings:
        """Parse the settings for the ODK form.

        Args:
            path: The path to where the XlsForm is stored
            workbook: The xlrd book object

        Returns:
            A Settings object
        """
        sheet = None
        try:
            sheet = workbook.sheet_by_name('settings')
        except xlrd.biffh.XLRDError:
            pass
        return Settings(path, sheet, workbook.datemode)

    def _associate_choice_lists(self) -> None:
        """Associate survey rows with their choice lists."""
        for row in self.survey:
            if row.is_select_type():
                list_name = row.get_select_list_name()
                # Future: how we get the list may change
                if row.is_select_external():
                    choice_list = self.choices.external_choices[list_name]
                else:
                    choice_list = self.choices.choices[list_name]
                row.choice_list = choice_list

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'OdkForm("{self.path}")'
        return msg
