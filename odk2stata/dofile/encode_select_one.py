from collections import namedtuple

from .do_file_section import DoFileSection
from .drop_column import DropColumn
from .rename import Rename
from .stata_utils import (get_varname_comments,
                          is_valid_stata_varname, label_define_do,
                          make_invalid_varname_comment, safe_stata_string_quote,
                          stata_string_escape)
from .templates import env
from ..dataset.column import Column
from ..dataset.dataset_collection import DatasetCollection
from ..odkform.choices import ChoiceList


LabelDefineOption = namedtuple('LabelDefineOption', ['number', 'label'])


ENCODE_SELECT_ONE_UNIT = env.get_template('encode_select_one_unit.do')
LABEL_DEFINE_UNIT = env.get_template('label_define_unit.do')


class EncodeSelectOne(DoFileSection):

    DEFAULT_SETTINGS = {
        'encode_select_ones': True,
        'encode_external_select_ones': False,
        'stata_columns_to_encode': [],
        'stata_columns_not_to_encode': [],
        'choice_lists_not_to_encode': [],
        'number_column': 'o2s_number',
        'strict_numbering': False,
        'label_replace_column': 'first_label',
    }

    def __init__(self, dataset_collection: DatasetCollection,
                 drop_column: DropColumn, rename: Rename, settings: dict,
                 populate: bool = False):
        self.select_ones = []
        self.drop_column = drop_column
        self.rename = rename
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        self.select_ones.clear()
        for column in self.dataset_collection:
            self.analyze_column(column)

    def analyze_column(self, column: Column):
        if self.should_encode(column):
            self.select_ones.append(column)

    def should_encode(self, column: Column):
        survey_row = column.survey_row
        if not survey_row.is_select_one():
            return False
        if self.drop_column.is_dropped_column(column):
            return False
        should_encode = False
        if survey_row.is_select_one():
            should_encode = self.encode_select_ones
        elif survey_row.is_select_external():
            should_encode = self.encode_external_select_ones
        if survey_row.choice_list.name in self.choice_lists_not_to_encode:
            should_encode = False
        if column.stata_varname in self.stata_columns_to_encode:
            should_encode = True
        if column.stata_varname in self.stata_columns_not_to_encode:
            should_encode = False
        return should_encode

    def do_file_iter(self):
        # 1. Make label define statements for all lists
        # 1a. Gather all unique lists
        choice_lists = self.get_unique_choice_lists()
        # 1b. Sort by name (something deterministic)
        sorted_choice_lists = sorted(list(choice_lists), key=lambda x: x.name)
        # 1c. Generate numbers and labels for each choice
        for choice_list in sorted_choice_lists:
            label_define_do = self.get_label_define_do(choice_list)
            yield label_define_do
        # 2. Encode each select_one
        # For each select_one that has been identified
        for column in self.select_ones:
            yield ''
            # Get the do file code to modify it
            encode_do = self.get_encode_do(column)
            # Yield the do file code
            yield encode_do
        if self.label_replace_column:
            yield ''
            for choice_list in sorted_choice_lists:
                label_replace_do = self.get_label_replace_do(choice_list)
                yield label_replace_do

    def get_label_define_do(self, choice_list: ChoiceList):
        # 1d. Combine and make the Stata statement
        list_varname = choice_list.name
        label_defines = self.get_label_define_options(choice_list)
        full_label_define = LABEL_DEFINE_UNIT.render(
            varname=list_varname,
            options_list=label_defines,
            replace=False
        )
        # 1e. Annotate what is an invalid Stata varname
        if not is_valid_stata_varname(list_varname):
            comment = make_invalid_varname_comment(list_varname)
            return f'{comment}\n{full_label_define}'
        return full_label_define

    def get_encode_do(self, column: Column):
        orig = self.rename.get_varname(column.stata_varname)
        gen = f'{orig}v2'
        lab = column.survey_row.choice_list.name
        comments = get_varname_comments(orig, gen)
        encode_do = ENCODE_SELECT_ONE_UNIT.render(
            orig=orig,
            gen=gen,
            lab=lab,
            comments=comments,
        )
        return encode_do

    def get_label_replace_do(self, choice_list: ChoiceList):
        list_varname = choice_list.name
        label_defines = self.get_label_replace_options(choice_list)
        full_label_define = LABEL_DEFINE_UNIT.render(
            varname=list_varname,
            options_list=label_defines,
            replace=True
        )
        if not is_valid_stata_varname(list_varname):
            comment = make_invalid_varname_comment(list_varname)
            return f'{comment}\n{full_label_define}'
        return full_label_define

    def get_unique_choice_lists(self):
        unique = set()
        for column in self.select_ones:
            choice_list = column.survey_row.choice_list
            unique.add(choice_list)
        return unique

    def get_label_define_options(self, choice_list: ChoiceList):
        result = []
        numbers = self.choice_list_numbers(choice_list)
        labels = self.choice_list_names(choice_list)
        for number, label in zip(numbers, labels):
            label_define = LabelDefineOption(number, label)
            result.append(label_define)
        return result

    def get_label_replace_options(self, choice_list: ChoiceList):
        result = []
        numbers = self.choice_list_numbers(choice_list)
        labels = self.choice_list_labels(choice_list)
        for number, label in zip(numbers, labels):
            label_define = LabelDefineOption(number, label)
            result.append(label_define)
        return result

    def choice_list_numbers(self, choice_list: ChoiceList):
        if self.strict_numbering:
            return self.choice_list_numbers_strict(choice_list)
        return self.choice_list_numbers_flexible(choice_list)

    def choice_list_numbers_strict(self, choice_list):
        if not self.number_column:
            msg = ('With strict choice numbering, a "number_column" must be '
                   'specified in settings')
            raise ValueError(msg)
        if self.number_column not in choice_list.row_header:
            msg = (f'Unable to find "{self.number_column}" in column headers '
                   f'for choice list "{choice_list.name}"')
            raise ValueError(msg)
        numbers = [row.row_dict[self.number_column] for row in choice_list]
        if any(not isinstance(i, int) for i in numbers):
            msg = (f'Choice list "{choice_list.name}" does not define all '
                   f'options to have a number in the "{self.number_column}" '
                   f'column')
            raise ValueError(msg)
        result = [str(i) for i in numbers]
        return result

    def choice_list_numbers_flexible(self, choice_list):
        result = []
        next_number = 1
        for choice in choice_list:
            name = choice.row_dict['name']
            number_column = choice.row_dict.get(self.number_column)
            if isinstance(number_column, int):
                value = number_column
            elif isinstance(name, int):
                value = name
            else:
                value = next_number
            result.append(str(value))
            next_number = max(next_number, value) + 1
        return result

    def choice_list_names(self, choice_list: ChoiceList):
        names = (str(choice.row_name) for choice in choice_list)
        result = [safe_stata_string_quote(name) for name in names]
        return result

    def choice_list_labels(self, choice_list: ChoiceList):
        result = []
        for choice in choice_list:
            label_replace_column = self.label_replace_column
            if label_replace_column == 'first_label':
                header = choice.row_header
                first_label = next(i for i in header if i.startswith('label'))
                label = choice.row_dict[first_label]
            elif label_replace_column in choice.row_dict:
                label = choice.row_dict[label_replace_column]
            else:
                msg = ('Encode select one should specify a value for '
                       '"label_replace_column" that is either "first_label", '
                       'or a column header in the choices/external_choices '
                       'tab. Instead, it is set to '
                       f'"{label_replace_column}".')
                raise ValueError(msg)
            label = str(label)
            escaped = stata_string_escape(label)
            result.append(escaped)
        return result

    @property
    def encode_select_ones(self):
        return self.settings['encode_select_ones']

    @property
    def encode_external_select_ones(self):
        return self.settings['encode_external_select_ones']

    @property
    def stata_columns_to_encode(self):
        return self.settings['stata_columns_to_encode']

    @property
    def stata_columns_not_to_encode(self):
        return self.settings['stata_columns_not_to_encode']

    @property
    def choice_lists_not_to_encode(self):
        return self.settings['choice_lists_not_to_encode']

    @property
    def number_column(self):
        return self.settings['number_column']

    @property
    def strict_numbering(self):
        """Return true if numbers should strictly come from number_column."""
        return self.settings['strict_numbering']

    @property
    def label_replace_column(self):
        """Get the column with the final labels.

        If this is the empty string, then the labels are not replaced.
        """
        return self.settings['label_replace_column']

    def __repr__(self):
        msg = f'<EncodeSelectOne, size {len(self.select_ones)}>'
        return msg
