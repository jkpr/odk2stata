from collections import namedtuple
from typing import List

from .do_file_section import DoFileSection
from .drop_column import DropColumn
from .rename import Rename
from .stata_utils import safe_stata_string_quote, varname_strip
from .templates import env
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.column import Column


BinaryLabel = namedtuple('BinaryLabel', ['zero', 'one'])
DEFAULT_YES_NO = BinaryLabel('No', 'Yes')


VarnameNameLabel = namedtuple('VarnameNameLabel', ['varname', 'name', 'label'])


SPLIT_SELECT_MULTIPLE_UNIT = env.get_template('split_select_multiple_unit.do')


class SplitSelectMultiple(DoFileSection):

    METHOD_APPEND_NAME = 'append_name'
    METHOD_APPEND_NUMBER = 'append_number'
    METHOD_NAME_ONLY = 'name_only'
    METHOD_NONE = 'none'
    ALLOWED_SPLIT_METHODS = (METHOD_APPEND_NAME, METHOD_APPEND_NUMBER,
                             METHOD_NAME_ONLY, METHOD_NONE)

    DEFAULT_EXCLUDE = 'numbers'
    DEFAULT_LABEL_DEFINE = 'yes_no'
    DEFAULT_LABEL_NAME = 'o2s_binary_label'

    DEFAULT_SETTINGS = {
        'default_split_method': METHOD_APPEND_NAME,
        'choices_to_exclude': '',
        'split_label': DEFAULT_LABEL_DEFINE,
        'binary_label_name': DEFAULT_LABEL_NAME,
        'choice_lists_to_split': [],
        'choice_lists_not_to_split': [],
        'stata_columns_to_split': [],
        'stata_columns_not_to_split': [],
        'stata_columns_to_append_name': [],
        'stata_columns_to_append_number': [],
        'stata_columns_to_name_only': [],
    }

    def __init__(self, dataset_collection: DatasetCollection,
                 drop_column: DropColumn, rename: Rename,
                 settings: dict = None, populate: bool = False):
        self.split_multiples = []
        self.drop_column = drop_column
        self.rename = rename
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        self.split_multiples.clear()
        for column in self.dataset_collection:
            self.analyze_column(column)

    def analyze_column(self, column: Column):
        if self.should_split(column):
            self.split_multiples.append(column)

    def should_split(self, column: Column) -> bool:
        row = column.survey_row
        if not row.is_select_multiple():
            return False
        elif self.drop_column.is_dropped_column(column):
            return False
        should_split = True
        if self.default_split_method == self.METHOD_NONE:
            should_split = False
        choice_list = row.choice_list.name
        if choice_list in self.choice_lists_to_split:
            should_split = True
        if choice_list in self.choice_lists_not_to_split:
            should_split = False
        stata_varname = column.stata_varname
        if stata_varname in self.stata_columns_to_split:
            should_split = True
        if stata_varname in self.stata_columns_not_to_split:
            should_split = False
        if should_split:
            return should_split
        if stata_varname in self.stata_columns_to_append_name:
            should_split = True
        if stata_varname in self.stata_columns_to_append_number:
            should_split = True
        if stata_varname in self.stata_columns_to_name_only:
            should_split = True
        return should_split

    def do_file_iter(self):
        yield self.binary_label_define_do()
        for column in self.split_multiples:
            yield ''
            yield self.split_select_multiple_do(column)

    def get_split_method(self, column: Column) -> str:
        split_method = self.default_split_method
        if column.stata_varname in self.stata_columns_to_append_name:
            split_method = self.METHOD_APPEND_NAME
        if column.stata_varname in self.stata_columns_to_append_number:
            split_method = self.METHOD_APPEND_NUMBER
        if column.stata_varname in self.stata_columns_to_name_only:
            split_method = self.METHOD_NAME_ONLY
        return split_method

    def get_binary_label(self) -> BinaryLabel:
        if self.split_label == self.DEFAULT_LABEL_DEFINE:
            return DEFAULT_YES_NO

    def binary_label_define_do(self):
        binary_label = self.get_binary_label()
        code = (f'label define {self.binary_label_name} 0 {binary_label[0]} 1 '
                f'{binary_label[1]}')
        return code

    def split_select_multiple_do(self, column: Column):
        orig = column.stata_varname
        padded = f'{orig}v2'
        varname_name_labels = self.get_varname_name_labels(column)
        first = varname_name_labels[0].varname
        last = varname_name_labels[-1].varname
        rendered = SPLIT_SELECT_MULTIPLE_UNIT.render(
            orig=orig,
            padded=padded,
            varname_name_labels=varname_name_labels,
            first=first,
            last=last,
            binary_label_name=self.binary_label_name,
        )
        return rendered

    def get_varname_name_labels(self, column: Column) \
            -> List[VarnameNameLabel]:
        result = []
        base_varname = self.rename.get_varname(column.stata_varname)
        survey_row = column.survey_row
        prompt_label = survey_row.get_label(self.which_label, self.extra_label)
        choice_list = survey_row.choice_list
        for choice in choice_list:
            name = choice.row_name
            if self.choices_to_exclude == 'numbers' and not \
                    isinstance(name, str):
                continue
            varname_unstripped = f'{base_varname}_{name}'
            varname = varname_strip(varname_unstripped)
            choice_label = choice.get_label(self.which_label, self.extra_label)
            label_unquoted = f'{prompt_label} : {choice_label}'
            label = safe_stata_string_quote(label_unquoted)
            combined = VarnameNameLabel(varname, name, label)
            result.append(combined)
        return result

    @property
    def default_split_method(self):
        result = self.settings['default_split_method']
        if result not in self.ALLOWED_SPLIT_METHODS:
            methods = (f'"{i}"' for i in self.ALLOWED_SPLIT_METHODS)
            methods = ', '.join(methods)
            msg = ('Under splitting select multiples, "default_split_method" '
                   f'is set to {result}. Please update to be one of {methods}.')
            raise ValueError(msg)
        return result

    @property
    def choices_to_exclude(self):
        result = self.settings['choices_to_exclude']
        return result

    @property
    def split_label(self):
        result = self.settings['split_label']
        if result != 'yes_no':
            msg = ('Under splitting select multiples, "split_label" must be '
                   '"yes_no". There are plans to allow other values here.')
            return NotImplementedError(msg)
        return result

    @property
    def binary_label_name(self):
        result = self.settings['binary_label_name']
        return result

    @property
    def choice_lists_to_split(self):
        result = self.settings['choice_lists_to_split']
        return result

    @property
    def choice_lists_not_to_split(self):
        result = self.settings['choice_lists_not_to_split']
        return result

    @property
    def stata_columns_to_split(self):
        result = self.settings['stata_columns_to_split']
        return result

    @property
    def stata_columns_not_to_split(self):
        result = self.settings['stata_columns_not_to_split']
        return result

    @property
    def stata_columns_to_append_name(self):
        result = self.settings['stata_columns_to_append_name']
        return result

    @property
    def stata_columns_to_append_number(self):
        result = self.settings['stata_columns_to_append_number']
        return result

    @property
    def stata_columns_to_name_only(self):
        result = self.settings['stata_columns_to_name_only']
        return result

    def __repr__(self):
        msg = f'<SplitSelectMultiple, size {len(self.split_multiples)}>'
        return msg
