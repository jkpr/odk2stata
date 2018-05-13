from collections import namedtuple
import re
import string
from typing import List

from ..odkform.survey import SurveyRow


StataRow = namedtuple('StataRow', ['stata_varname', 'survey_row'])


# TODO - remove all instances of this
def survey_to_stata_row(survey_row: SurveyRow) -> StataRow:
    column_name = survey_row.get_column_name()
    stata_varname = clean_stata_varname(column_name)
    return StataRow(stata_varname, survey_row)


def clean_stata_varname(column_name: str) -> str:
    cleaned = varname_strip(column_name)
    truncated = varname_truncate(cleaned)
    return truncated


def gen_anonymous_varname(column_number: int) -> str:
    return f'v{column_number + 1}'


STATA_VARNAME_REGEX = '[_a-zA-Z][_a-zA-Z0-9]{,31}'
STATA_VARNAME_REGEX_PROG = re.compile(STATA_VARNAME_REGEX)


def is_valid_stata_varname(varname: str) -> bool:
    valid = bool(STATA_VARNAME_REGEX_PROG.fullmatch(varname))
    return valid


def gen_valid_stata_varname(varname: str) -> str:
    _varname = varname
    if _varname and not re.match(_varname[0], '[_a-zA-Z]'):
        _varname = f'C{_varname}'
    _varname = ''.join(i for i in _varname if re.match(i, '[_a-zA-Z0-9]'))
    if len(_varname) > 32:
        _varname = _varname[:32]
    return _varname


def safe_stata_string_quote(text: str) -> str:
    if '"' in text:
        # Compound double quotes
        return f"""`"{text}"'"""
    return f'"{text}"'


def stata_string_escape(text: str) -> str:
    new_text = text
    new_text = new_text.replace('\n', '\\n')
    new_text = new_text.replace('\t', '\\t')
    new_text = new_text.replace('"', "'")
    return f'"{new_text}"'


VARNAME_CHARACTERS = set(string.ascii_letters + string.digits + '_')


def varname_strip(varname: str) -> str:
    new_varname = ''.join(i for i in varname if i in VARNAME_CHARACTERS)
    return new_varname


def varname_truncate(varname: str) -> str:
    if len(varname) > 32:
        return varname[:32]
    return varname


LabelDefineOption = namedtuple('LabelDefineOption', ['number', 'label'])


def label_define_do(varname: str, options_list: List[LabelDefineOption],
                    replace: bool = False) -> str:
    options = (' '.join(i) for i in options_list)
    full_options_list = ' '.join(options)
    replace_chunk = ', replace' if replace else ''
    full_do = f'label define {varname} {full_options_list}{replace_chunk}'
    return full_do


def make_invalid_varname_comment(varname: str):
    return f'* Invalid STATA varname: {varname}'


def get_varname_comments(*args):
    comments = [make_invalid_varname_comment(i) for i in args if not
                is_valid_stata_varname(i)]
    return comments
