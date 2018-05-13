from ..odkform.survey import SurveyRow


class Column:

    def __init__(self, column_number: int, column_name: str,
                 stata_varname: str, survey_row: SurveyRow):
        self.column_number = column_number
        self.column_name = column_name
        self.stata_varname = stata_varname
        self.survey_row = survey_row

    def __repr__(self):
        msg = (f'Column({self.column_number}, "{self.dataset_name}", '
               f'"{self.stata_varname}", {repr(self.survey_row)})')
        return msg
