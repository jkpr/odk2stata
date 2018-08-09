"""A module defining the Column class."""
from ..odkform.survey import SurveyRow


class Column:
    """Describe a column in the dataset.

    Instance attributes:
        column_name: The column name in the original CSV
        survey_row: The SurveyRow associated with this Column
        repeat_dataset: The repeat group Dataset associated with this
            column, if there is one.
    """

    def __init__(self, column_name: str, survey_row: SurveyRow):
        """Initialize a Column instance.

        Args:
            column_name: The column name in the original CSV
            survey_row: The SurveyRow associated with this Column
        """
        self.column_name = column_name
        self.survey_row = survey_row
        self.repeat_dataset = None

    def __hash__(self):
        """Make a hash based on the column name and the survey row."""
        return hash((self.column_name, self.survey_row))

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'Column({self.column_name}, {self.survey_row!r})'
        return msg
