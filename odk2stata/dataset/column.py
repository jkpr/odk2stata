"""A module defining the Column class."""
from ..odkform.survey import SurveyRow


class Column:
    """Describe a column in the dataset.

    Instance attributes:
        column_number: The 0-indexed column number
        column_name: The column name in the original CSV
        stata_varname: The column name after being imported to Stata.
            This is a best-attempt calculation.
        survey_row: The SurveyRow associated with this Column
    """

    def __init__(self, column_number: int, column_name: str,
                 stata_varname: str, survey_row: SurveyRow):
        """Initialize a Column instance.

        Args:
            column_number: The 0-indexed column number
            column_name: The column name in the original CSV
            stata_varname: The column name after being imported to Stata.
                This is a best-attempt calculation.
            survey_row: The SurveyRow associated with this Column
        """
        self.column_number = column_number
        self.column_name = column_name
        self.stata_varname = stata_varname
        self.survey_row = survey_row

    def __repr__(self):
        """Get a representation of this object."""
        msg = (f'Column({self.column_number}, "{self.dataset_name}", '
               f'"{self.stata_varname}", {self.survey_row!r})')
        return msg
