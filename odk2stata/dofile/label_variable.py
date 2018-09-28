from .do_file_section import DoFileSection
from .imported_dataset import ImportedDataset, StataVar
from .stata_utils import stata_string_escape


MAX_LABEL_LEN = 80


class LabelVariable(DoFileSection):

    DEFAULT_SETTINGS = {
        'first_paragraph_only': False,
        'remove_numbering': True,
        'stop_at_words': [],
        'stop_before_words': [],
    }

    def __init__(self, dataset: ImportedDataset, settings: dict = None,
                 populate: bool = False):
        self.label_variables = []
        super().__init__(dataset, settings, populate)

    def populate(self):
        self.label_variables.clear()
        for var in self.dataset:
            self.analyze_variable(var)

    def analyze_variable(self, var: StataVar):
        if self.should_label(var):
            self.label_variables.append(var)

    def should_label(self, var: StataVar):
        if var.is_dropped() or var.column.survey_row is None:
            return False
        if var.column.survey_row.becomes_column():
            return True
        return False

    def do_file_iter(self):
        for var in self.label_variables:
            yield self.label_variable_do(var)

    def label_variable_do(self, var: StataVar):
        varname = var.varname
        label_raw = var.column.survey_row.get_label(self.which_label,
                                                    self.extra_label)
        label_cleaned = self.clean_label(label_raw)
        if label_cleaned == '':
            return f'* LABEL SKIPPED: variable "{varname}" has no label.'
        # TODO IMPROVE THIS PART
        label_truncated = label_cleaned[:MAX_LABEL_LEN]
        label = stata_string_escape(label_truncated)
        label_variable = f'label var {varname} {label}'
        if len(label_cleaned) > 80:
            msg = (f'* LABEL TOO LONG: original label is {len(label_cleaned)} characters long. '
                   f'the last {len(label_cleaned) - 80} characters will be lost.')
            label_variable = f'{msg}\n{label_variable}'
        return label_variable

    def clean_label(self, text: str) -> str:
        new_text = text
        if self.remove_numbering:
            new_text = self.get_number_removed(text)
        return new_text

    @staticmethod
    def get_number_removed(text: str) -> str:
        split = text.split(maxsplit=1)
        if len(split) > 1 and any(ch.isdigit() for ch in split[0]):
            return split[1]
        return text

    @property
    def remove_numbering(self):
        result = self.settings['remove_numbering']
        return result

    def __repr__(self):
        """Get a representation of this object."""
        msg = f"<LabelVariable, size {len(self.label_variables)}>"
        return msg
