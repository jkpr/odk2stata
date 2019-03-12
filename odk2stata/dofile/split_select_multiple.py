from collections import namedtuple
from dataclasses import dataclass
from typing import List

from .do_file_section import DoFileSection
from .imported_dataset import ImportedDataset, StataVar
from .stata_utils import (clean_stata_varname, gen_tmp_varname,
                          stata_string_escape, strip_non_alphanum,
                          varname_strip, VARNAME_MAX_LEN, LABEL_MAX_LEN)
from .templates import env
from ..odkform.choices import NumberNameChoice


@dataclass(frozen=True)
class SplitSettings:
    """General settings related to individual splits."""
    choices_to_exclude: str
    which_label: str
    extra_label: str
    strict_numbering: bool
    number_column: str


@dataclass(frozen=True)
class GenBinary:
    """Data needed to define a generated binary variable."""
    original_varname: str
    padded_varname: str
    choice_name: str
    binary_varname: str
    binary_label: str


@dataclass(frozen=True)
class NumberNameLabel:
    """Relevant data about choice options."""
    number: int
    name: str
    label: str


SPLIT_SELECT_MULTIPLE_UNIT = env.get_template('split_select_multiple_unit.do')


class SsmUnit:

    def __init__(self, select_multiple: StataVar, split_method: str,
                 binary_label: str, split_settings: SplitSettings):
        self.select_multiple = select_multiple
        self.split_method = split_method
        self.binary_label = binary_label
        self.split_settings = split_settings

        self.original_varname = self.select_multiple.varname
        self.padded_varname = gen_tmp_varname(self.original_varname)
        self.select_multiple_label = self.get_select_multiple_label()
        self.choices = self.get_choices()
        self.gen_binaries = self.get_gen_binaries()

    def get_select_multiple_label(self) -> str:
        """Get the desired label for the select_multiple"""
        survey_row = self.select_multiple.get_survey_row()
        prompt_label = survey_row.get_label(self.split_settings.which_label,
                                            self.split_settings.extra_label)
        return prompt_label

    def get_choices(self) -> List[NumberNameLabel]:
        """Get filtered choices based on choices_to_exclude."""
        #import pdb; pdb.set_trace()
        exclude = self.split_settings.choices_to_exclude
        exclude_numbers = exclude == SplitSelectMultiple.CHOICE_EXCLUDE_NUMBERS
        exclude_negative_numbers = exclude == \
            SplitSelectMultiple.CHOICE_EXCLUDE_NEGATIVE_NUMBERS
        all_choices = self.get_all_choices()
        result = []
        for number, name, choice in all_choices:
            try:
                int_name = int(name)
                if exclude_numbers:
                    continue
                elif exclude_negative_numbers and int_name < 0:
                    continue
            except ValueError:
                pass
            label = choice.get_label(self.split_settings.which_label,
                                     self.split_settings.extra_label)
            result.append(NumberNameLabel(number, name, label))
        return result

    def get_all_choices(self) -> List[NumberNameChoice]:
        """Get all choices and their numbers and names."""
        choice_list = self.select_multiple.get_survey_row().choice_list
        number_column = self.split_settings.number_column
        if self.split_settings.strict_numbering:
            return choice_list.get_choices_strictly_numbered(number_column)
        else:
            return choice_list.get_choices_flexibly_numbered(number_column)

    def get_gen_binaries(self):
        """Get the GenBinary objects for this unit."""
        gen_binaries = []
        names = (choice.name for choice in self.choices)
        binary_varnames = self.gen_varnames()
        binary_labels = self.gen_labels()
        zipped = zip(names, binary_varnames, binary_labels)
        for choice_name, binary_varname, binary_label in zipped:
            gen_binary = GenBinary(self.original_varname, self.padded_varname,
                                   choice_name, binary_varname, binary_label)
            gen_binaries.append(gen_binary)
        return gen_binaries

    def gen_varnames(self) -> List[str]:
        split_method = self.split_method
        if split_method == SplitSelectMultiple.METHOD_APPEND_NAME:
            return self.gen_varnames_append_name()
        elif split_method == SplitSelectMultiple.METHOD_APPEND_NUMBER:
            return self.gen_varnames_append_number()
        elif split_method == SplitSelectMultiple.METHOD_NAME_ONLY:
            return self.gen_varnames_name_only()
        else:
            raise ValueError(split_method)

    def gen_varnames_append_name(self) -> List[str]:
        suffixes = []
        for choice in self.choices:
            name = choice.name
            uncut_suffix = strip_non_alphanum(name)
            suffix = uncut_suffix[:(VARNAME_MAX_LEN - 2)]
            suffixes.append(suffix)
        max_len = max(len(suffix) for suffix in suffixes)
        uncut_stem = clean_stata_varname(self.original_varname)
        stem = uncut_stem[:(VARNAME_MAX_LEN - max_len - 1)]
        varnames = [f'{stem}_{suffix}' for suffix in suffixes]
        return varnames

    def gen_varnames_append_number(self) -> List[str]:
        suffixes = []
        for choice in self.choices:
            number = choice.number
            suffix = str(abs(number))
            suffixes.append(suffix)
        max_len = max(len(suffix) for suffix in suffixes)
        uncut_stem = clean_stata_varname(self.original_varname)
        stem = uncut_stem[:(VARNAME_MAX_LEN - max_len - 1)]
        varnames = [f'{stem}_{suffix}' for suffix in suffixes]
        return varnames

    def gen_varnames_name_only(self) -> List[str]:
        return [clean_stata_varname(item.name) for item in self.choices]

    def gen_labels(self) -> List[str]:
        gen_labels = []
        uncut_stem = self.select_multiple_label
        for choice in self.choices:
            label = choice.label
            suffix = label
            stem_len = LABEL_MAX_LEN - (len(suffix) + 3)
            stem = uncut_stem[:stem_len]
            gen_label = ' : '.join((stem, suffix))
            gen_labels.append(stata_string_escape(gen_label))
        return gen_labels

    def render(self) -> str:
        rendered = SPLIT_SELECT_MULTIPLE_UNIT.render(
            orig=self.original_varname,
            padded=self.padded_varname,
            gen_binaries=self.gen_binaries,
            first=self.first,
            last=self.last,
            binary_label=self.binary_label,
        )
        return rendered

    @property
    def first(self) -> str:
        """Get the varname of the first choice option."""
        if not self.gen_binaries:
            return None
        return self.gen_binaries[0].binary_varname

    @property
    def last(self) -> str:
        """Get the varname of the last choice option."""
        if not self.gen_binaries:
            return None
        return self.gen_binaries[-1].binary_varname

    def __repr__(self):
        """Get a representation of this object."""
        return f'<SsmUnit "{self.select_multiple!r}">'


@dataclass(frozen=True)
class VarMethod:
    """A container for a select_multiple and its split method."""
    select_multiple: StataVar
    split_method: str


@dataclass(frozen=True)
class BinaryOptionLabel:
    zero: str
    one: str


@dataclass(frozen=True)
class BinaryDefine:
    label: str
    option_label: BinaryOptionLabel


class SsmDetails:

    def __init__(self, var_methods : List[VarMethod],
                 binary_define: BinaryDefine, split_settings: SplitSettings):
        self.var_methods = var_methods
        self.binary_define = binary_define
        self.split_settings = split_settings

        self.ssm_units = self.get_ssm_units()

    def get_ssm_units(self) -> List[SsmUnit]:
        ssm_units = []
        binary_label = self.binary_define.label
        for var_method in self.var_methods:
            select_multiple = var_method.select_multiple
            split_method = var_method.split_method
            ssm_unit = SsmUnit(select_multiple, split_method, binary_label,
                               self.split_settings)
            ssm_units.append(ssm_unit)
        return ssm_units


DEFAULT_YES_NO = BinaryOptionLabel('No', 'Yes')


VarnameNameLabel = namedtuple('VarnameNameLabel', ['varname', 'name', 'label'])


class SplitSelectMultiple(DoFileSection):

    METHOD_APPEND_NAME = 'append_name'
    METHOD_APPEND_NUMBER = 'append_number'
    METHOD_NAME_ONLY = 'name_only'
    METHOD_NONE = 'none'
    ALLOWED_SPLIT_METHODS = (
        METHOD_APPEND_NAME,
        METHOD_APPEND_NUMBER,
        METHOD_NAME_ONLY,
        METHOD_NONE
    )

    DEFAULT_BINARY_OPTION_LABEL = 'yes_no'
    DEFAULT_BINARY_LABEL = 'o2s_binary_label'

    CHOICE_EXCLUDE_NUMBERS = 'numbers'
    CHOICE_EXCLUDE_NEGATIVE_NUMBERS = 'negative_numbers'
    CHOICE_EXCLUDE_NONE = 'none'
    ALLOWED_CHOICE_EXCLUDES = (
        CHOICE_EXCLUDE_NUMBERS,
        CHOICE_EXCLUDE_NEGATIVE_NUMBERS,
        CHOICE_EXCLUDE_NONE
    )

    DEFAULT_NUMBER_COLUMN = 'o2s_number'

    DEFAULT_SETTINGS = {
        'default_split_method': METHOD_APPEND_NUMBER,
        'binary_option_label': DEFAULT_BINARY_OPTION_LABEL,
        'binary_label': DEFAULT_BINARY_LABEL,
        'choices_to_exclude': CHOICE_EXCLUDE_NEGATIVE_NUMBERS,
        'choice_lists_to_split': [],
        'choice_lists_not_to_split': [],
        'odk_names_to_split': [],
        'odk_names_not_to_split': [],
        'odk_names_to_append_name': [],
        'odk_names_to_append_number': [],
        'odk_names_to_name_only': [],
        'number_column': DEFAULT_NUMBER_COLUMN,
        'strict_numbering': False,
    }

    def __init__(self, dataset: ImportedDataset, settings: dict = None,
                 populate: bool = False):
        self.select_multiples = []
        super().__init__(dataset, settings, populate)

    def populate(self):
        self.select_multiples.clear()
        for var in self.dataset:
            self.analyze_variable(var)

    def analyze_variable(self, var: StataVar):
        if self.should_split(var):
            self.select_multiples.append(var)

    def should_split(self, var: StataVar) -> bool:
        if var.is_dropped():
            return False
        row = var.get_survey_row()
        if row is None:
            return False
        elif not row.is_select_multiple():
            return False
        should_split = True
        if self.default_split_method == self.METHOD_NONE:
            should_split = False
        choice_list = row.choice_list.name
        if choice_list in self.choice_lists_to_split:
            should_split = True
        if choice_list in self.choice_lists_not_to_split:
            should_split = False
        odk_name = var.get_odk_name()
        if odk_name in self.odk_names_to_split:
            should_split = True
        if odk_name in self.odk_names_not_to_split:
            should_split = False
        if odk_name in self.odk_names_to_append_name:
            should_split = True
        if odk_name in self.odk_names_to_append_number:
            should_split = True
        if odk_name in self.odk_names_to_name_only:
            should_split = True
        return should_split

    def do_file_iter(self):
        yield ''

    def get_ssm_details(self) -> SsmDetails:
        var_methods = []
        for select_multiple in self.select_multiples:
            split_method = self.get_split_method(select_multiple)
            if split_method == self.METHOD_NONE:
                continue
            var_method = VarMethod(select_multiple, split_method)
            var_methods.append(var_method)
        binary_define = self.get_binary_define()
        split_settings = SplitSettings(
            self.choices_to_exclude,
            self.which_label,
            self.extra_label,
            self.strict_numbering,
            self.number_column,
        )
        ssm_details = SsmDetails(var_methods, binary_define, split_settings)
        return ssm_details

    def get_split_method(self, var: StataVar) -> str:
        split_method = self.default_split_method
        odk_name = var.get_odk_name()
        if odk_name in self.odk_names_to_append_name:
            split_method = self.METHOD_APPEND_NAME
        if odk_name in self.odk_names_to_append_number:
            split_method = self.METHOD_APPEND_NUMBER
        if odk_name in self.odk_names_to_name_only:
            split_method = self.METHOD_NAME_ONLY
        return split_method

    def get_binary_define(self) -> BinaryDefine:
        binary_label = self.binary_label
        binary_option_label = self.get_binary_option_label()
        binary_define = BinaryDefine(binary_label, binary_option_label)
        return binary_define

    def get_binary_option_label(self) -> BinaryOptionLabel:
        if self.binary_option_label == self.DEFAULT_BINARY_OPTION_LABEL:
            return DEFAULT_YES_NO
        raise ValueError(self.binary_option_label)

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
        if result not in self.ALLOWED_CHOICE_EXCLUDES:
            methods = (f'"{i}"' for i in self.ALLOWED_CHOICE_EXCLUDES)
            methods = ', '.join(methods)
            msg = ('Under splitting select multiples, "choices_to_exclude" '
                   f'is set to {result}. Please update to be one of {methods}.')
            raise ValueError(msg)
        return result

    @property
    def binary_option_label(self):
        result = self.settings['binary_option_label']
        if result != self.DEFAULT_BINARY_OPTION_LABEL:
            msg = ('Under splitting select multiples, "binary_option_label" '
                   'must be '
                   '"yes_no". There are plans to allow other values here.')
            return NotImplementedError(msg)
        return result

    @property
    def binary_label(self):
        result = self.settings['binary_label']
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
    def odk_names_to_split(self):
        result = self.settings['odk_names_to_split']
        return result

    @property
    def odk_names_not_to_split(self):
        result = self.settings['odk_names_not_to_split']
        return result

    @property
    def odk_names_to_append_name(self):
        result = self.settings['odk_names_to_append_name']
        return result

    @property
    def odk_names_to_append_number(self):
        result = self.settings['odk_names_to_append_number']
        return result

    @property
    def odk_names_to_name_only(self):
        result = self.settings['odk_names_to_name_only']
        return result

    @property
    def number_column(self):
        return self.settings['number_column']

    @property
    def strict_numbering(self):
        """Return true if numbers should strictly come from number_column."""
        return self.settings['strict_numbering']

    def __repr__(self):
        msg = f'<SplitSelectMultiple, size {len(self.select_multiples)}>'
        return msg
