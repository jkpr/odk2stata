from collections import defaultdict, namedtuple
from typing import List
import textwrap

from .do_file_section import DoFileSection
from .imported_dataset import ImportedDataset, StataVar
from .stata_utils import (get_varname_comments, is_valid_stata_varname,
                          make_invalid_varname_comment, safe_stata_string_quote,
                          stata_string_escape)
from .templates import env
from ..odkform.choices import ChoiceList


class EncodeSelectOne(DoFileSection):

    DEFAULT_SETTINGS = {
        'encode_select_ones': True,
        'encode_external_select_ones': False,
        'odk_names_to_encode': [],
        'odk_names_not_to_encode': [],
        'choice_lists_not_to_encode': [],
        'number_column': 'o2s_number',
        'strict_numbering': False,
        'label_replace_column': 'first_label',
    }

    def __init__(self, dataset: ImportedDataset, settings: dict,
                 populate: bool = False):
        self.select_ones: List[StataVar] = []
        super().__init__(dataset, settings, populate)

    def populate(self):
        self.select_ones.clear()
        for var in self.dataset:
            self.analyze_variable(var)

    def analyze_variable(self, var: StataVar):
        if self.should_encode(var):
            self.select_ones.append(var)

    def should_encode(self, var: StataVar):
        survey_row = var.column.survey_row
        if survey_row is None:
            return False
        if not survey_row.is_select_one():
            return False
        if var.is_dropped():
            return False
        should_encode = self.encode_select_ones
        if survey_row.is_select_external():
            should_encode = self.encode_external_select_ones
        if survey_row.choice_list.name in self.choice_lists_not_to_encode:
            should_encode = False
        if var.get_odk_name() in self.odk_names_to_encode:
            should_encode = True
        if var.get_odk_name() in self.odk_names_not_to_encode:
            should_encode = False
        return should_encode

    def get_encode_details(self):
        details = EncodeDetails(
            self.select_ones,
            self.number_column,
            self.strict_numbering,
            self.which_label,
            self.extra_label,
        )
        return details

    def do_file_iter(self):
        # TODO: I don't like this method of getting the do-code
        details = self.get_encode_details()
        yield details.get_encode_select_one_do()

    @property
    def encode_select_ones(self):
        return self.settings['encode_select_ones']

    @property
    def encode_external_select_ones(self):
        return self.settings['encode_external_select_ones']

    @property
    def odk_names_to_encode(self):
        return self.settings['odk_names_to_encode']

    @property
    def odk_names_not_to_encode(self):
        return self.settings['odk_names_not_to_encode']

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

    def __repr__(self):
        """Get a representation of this object."""
        msg = f'<EncodeSelectOne, size {len(self.select_ones)}>'
        return msg


class EncodeDetails:

    def __init__(self, select_ones: List[StataVar], number_column: str,
                 strict_numbering: bool, which_label: str, extra_label: str):
        self.select_ones = select_ones
        choice_lists = self.get_unique_choice_lists()
        sorted_choice_lists = sorted(list(choice_lists), key=lambda x: x.name)
        encode_choice_list_lookup = {}
        self.encode_choice_lists = []
        for choice_list in sorted_choice_lists:
            encode_choice_list = EncodeChoiceList(
                choice_list,
                number_column,
                strict_numbering,
                which_label,
                extra_label
            )
            self.encode_choice_lists.append(encode_choice_list)
            encode_choice_list_lookup[choice_list] = encode_choice_list
        self.encode_singleton = []
        sorted_select_ones = defaultdict(list)
        for select_one in self.select_ones:
            choice_list = select_one.column.survey_row.choice_list
            if len(select_one.varname) > 30:
                encode_choice_list = encode_choice_list_lookup[choice_list]
                encode_singleton = EncodeSingleton(select_one,
                                                   encode_choice_list)
                self.encode_singleton.append(encode_singleton)
            else:
                sorted_select_ones[choice_list].append(select_one)
        self.encode_for = []
        for key, value in sorted_select_ones.items():
            encode_choice_list = encode_choice_list_lookup[key]
            if len(value) > 1:
                encode_for = EncodeFor(value, encode_choice_list)
                self.encode_for.append(encode_for)
            else:
                encode_singleton = EncodeSingleton(value[0], encode_choice_list)
                self.encode_singleton.append(encode_singleton)

    def get_unique_choice_lists(self):
        unique = set()
        for var in self.select_ones:
            choice_list = var.column.survey_row.choice_list
            unique.add(choice_list)
        return unique

    def get_encode_select_one_do(self):
        label_define = '\n'.join((
            item.get_label_define_do() for item in self.encode_choice_lists
        ))
        singletons = '\n\n'.join((
            item.get_singleton_do() for item in self.encode_singleton
        ))
        foreach = '\n\n'.join((
            item.get_for_do() for item in self.encode_for
        ))
        label_replace = '\n'.join((
            item.get_label_replace_do() for item in self.encode_choice_lists
        ))
        return '\n\n'.join([label_define, singletons, foreach, label_replace])


LabelDefineOption = namedtuple('LabelDefineOption', ['number', 'label'])
LABEL_DEFINE_UNIT = env.get_template('label_define_unit.do')


class EncodeChoiceList:

    def __init__(self, choice_list: ChoiceList, number_column: str,
                 strict_numbering: bool, which_label: str, extra_label: str):
        self.choice_list = choice_list
        self.list_name = self.get_list_name()
        self.number_column = number_column
        self.strict_numbering = strict_numbering
        self.which_label = which_label
        self.extra_label = extra_label

    def get_list_name(self):
        # TODO: self.choice_list.name may not be valid
        return self.choice_list.name

    def get_label_define_do(self) -> str:
        list_varname = self.list_name
        label_defines = self.get_label_define_options()
        full_label_define = LABEL_DEFINE_UNIT.render(
            varname=list_varname,
            options_list=label_defines,
            replace=False
        )
        return full_label_define

    def get_label_replace_do(self) -> str:
        list_varname = self.list_name
        label_defines = self.get_label_replace_options()
        full_label_define = LABEL_DEFINE_UNIT.render(
            varname=list_varname,
            options_list=label_defines,
            replace=True
        )
        return full_label_define

    def get_label_define_options(self):
        result = []
        numbers = self.choice_list_numbers()
        labels = self.choice_list_names()
        for number, label in zip(numbers, labels):
            label_define = LabelDefineOption(number, label)
            result.append(label_define)
        return result

    def get_label_replace_options(self):
        result = []
        numbers = self.choice_list_numbers()
        labels = self.choice_list_labels()
        for number, label in zip(numbers, labels):
            label_define = LabelDefineOption(number, label)
            result.append(label_define)
        return result

    def choice_list_numbers(self):
        if self.strict_numbering:
            return self.choice_list_numbers_strict()
        return self.choice_list_numbers_flexible()

    def choice_list_numbers_strict(self):
        if not self.number_column:
            msg = ('With strict choice numbering, a "number_column" must be '
                   'specified in settings')
            raise ValueError(msg)
        if self.number_column not in self.choice_list.row_header:
            msg = (f'Unable to find "{self.number_column}" in column headers '
                   f'for choice list "{choice_list.name}"')
            raise ValueError(msg)
        numbers = [row.row_dict[self.number_column] for row in self.choice_list]
        if any(not isinstance(i, int) for i in numbers):
            msg = (f'Choice list "{self.choice_list.name}" does not define all '
                   f'options to have a number in the "{self.number_column}" '
                   f'column')
            raise ValueError(msg)
        result = [str(i) for i in numbers]
        return result

    def choice_list_numbers_flexible(self):
        result = []
        next_number = 1
        for choice in self.choice_list:
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

    def choice_list_names(self):
        names = (str(choice.row_name) for choice in self.choice_list)
        result = [safe_stata_string_quote(name) for name in names]
        return result

    def choice_list_labels(self):
        result = []
        for choice in self.choice_list:
            which_label = self.which_label
            if which_label == 'first_label':
                header = choice.row_header
                first_label = next(i for i in header if i.startswith('label'))
                label = choice.row_dict[first_label]
            elif which_label in choice.row_dict:
                label = choice.row_dict[which_label]
            else:
                msg = ('Encode select one should specify a value for '
                       '"label_replace_column" that is either "first_label", '
                       'or a column header in the choices/external_choices '
                       'tab. Instead, it is set to '
                       f'"{label_replace_column}".')
                raise ValueError(msg)
            final_label = str(label)
            extra_label = choice.row_dict.get(self.extra_label, '')
            if extra_label != '':
                final_label = str(extra_label)
            escaped = stata_string_escape(final_label)
            result.append(escaped)
        return result


ENCODE_SELECT_ONE_UNIT = env.get_template('encode_select_one_unit.do')


class EncodeSingleton:

    def __init__(self, select_one: StataVar,
                 encode_choice_list: EncodeChoiceList):
        self.select_one = select_one
        self.encode_choice_list = encode_choice_list

    def get_singleton_do(self) -> str:
        orig = self.select_one.varname
        gen = f'{orig[:30]}V2'
        lab = self.encode_choice_list.list_name
        singleton_do = ENCODE_SELECT_ONE_UNIT.render(
            orig=orig,
            gen=gen,
            lab=lab,
        )
        return singleton_do


ENCODE_SELECT_ONE_FOR_UNIT = env.get_template('encode_select_one_for_unit.do')


class EncodeFor:

    STATA_FOR_VAR = 'var'
    SUFFIX = 'V2'
    WIDTH = 120

    def __init__(self, select_ones: List[StataVar],
                 encode_choice_list: EncodeChoiceList):
        self.select_ones = select_ones
        self.encode_choice_list = encode_choice_list

    def get_foreach_line(self, stata_var, width=WIDTH):
        intro = f'foreach {stata_var} in '
        intro_width = len(intro)
        wrap_width = width - intro_width
        joined_varnames = ' '.join((var.varname for var in self.select_ones))
        subsequent = ' ' * intro_width
        wrapped = textwrap.wrap(joined_varnames, width=wrap_width,
                                initial_indent=intro,
                                subsequent_indent=subsequent)
        joined_wrapped = ' ///\n'.join(wrapped)
        complete_text = f'{joined_wrapped} '
        return complete_text

    def get_for_do(self, stata_var=STATA_FOR_VAR, suffix=SUFFIX) -> str:
        foreach = self.get_foreach_line(stata_var)
        lab = self.encode_choice_list.list_name
        for_do = ENCODE_SELECT_ONE_FOR_UNIT.render(
            foreach=foreach,
            lab=lab,
            var=stata_var,
            suffix=suffix,
        )
        return for_do
