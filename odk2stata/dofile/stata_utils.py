"""A collection of useful Stata-related functions.

Module attributes:
    STATA_VARNAME_REGEX: A regular expression for Stata varnames
    STATA_VARNAME_REGEX_PROG: A compiled regular expression for Stata
        varnames based on STATA_VARNAME_REGEX
    VARNAME_CHARACTERS: The full set of valid Stata varname characters
    LabelDefineOption: A named tuple with number and label attributes.
        This is used for encoding select_one variables.
"""
import re
import string


def clean_stata_varname(column_name: str) -> str:
    """Clean a Stata varname.

    Strip out bad characters first, then truncate to 32 characters.

    Args:
        column_name: An uncleaned column name

    Returns:
        A cleaned Stata varname
    """
    cleaned = varname_strip(column_name)
    letter_start = varname_valid_start(cleaned)
    truncated = varname_truncate(letter_start)
    return truncated


VARNAME_CHARACTERS = set(string.ascii_letters + string.digits + '_')


def varname_strip(varname: str) -> str:
    """Strip out invalid characters from a Stata varname."""
    new_varname = ''.join(i for i in varname if i in VARNAME_CHARACTERS)
    return new_varname


VARNAME_START_CHARACTERS = set(string.ascii_letters + '_')


def varname_valid_start(varname: str) -> str:
    """Ensure a Stata varname starts with a letter.

    This routine checks the first character of a supplied varname, and
    if needed, it prepends a 'v' at the beginning and returns.

    A valid first character is in the class [_a-zA-Z].
    """
    if varname == '':
        return 'v'
    new_varname = varname
    first_char = new_varname[0]
    if first_char not in VARNAME_START_CHARACTERS:
        new_varname = f'v{new_varname}'
    return new_varname


VARNAME_MAX_LEN = 32
LABEL_MAX_LEN = 80


def varname_truncate(varname: str) -> str:
    """Truncate a Stata varname down to 32 characters, if needed."""
    if len(varname) > VARNAME_MAX_LEN:
        return varname[:VARNAME_MAX_LEN]
    return varname


ALPHANUM_CHARACTERS = set(string.ascii_letters + string.digits)


def strip_non_alphanum(varname: str) -> str:
    """Strip out non-alphanumeric characters from a Stata varname."""
    new_varname = ''.join(i for i in varname if i in ALPHANUM_CHARACTERS)
    return new_varname


def gen_anonymous_varname(column_number: int) -> str:
    """Generate a Stata varname based on the column number.

    Stata columns are 1-indexed.
    """
    return f'v{column_number}'


def gen_tmp_varname(varname: str) -> str:
    """Generate a temporary Stata varname based on a given varname."""
    stem = varname[:30]
    return f'{stem}V2'


STATA_VARNAME_REGEX = '[_a-zA-Z][_a-zA-Z0-9]{,31}'
STATA_VARNAME_REGEX_PROG = re.compile(STATA_VARNAME_REGEX)


def is_valid_stata_varname(varname: str) -> bool:
    """Return True if and only if varname is valid in Stata.

    Currently, this function checks against the basic regular
    expression. In the future, it will check against a list of
    prohibited Stata varnames, according to Stata documentation.
    """
    valid = bool(STATA_VARNAME_REGEX_PROG.fullmatch(varname))
    return valid


def safe_stata_string_quote(text: str) -> str:
    """Safely quote a string for Stata.

    Use this when the string should not be changed.

    Args:
        text: A string for a Stata argument

    Returns:
        A quoted string. If there is a quotation mark, then we make use
        of Stata compound quotation marks.
    """
    if '"' in text:
        # Compound double quotes
        return f"""`"{text}"'"""
    return f'"{text}"'


def stata_string_escape(text: str) -> str:
    """Escape a string for Stata.

    Use this when a string needs to be escaped for a single line.

    Args:
        text: A string for a Stata argument

    Returns:
        A quoted string.
    """
    new_text = text
    new_text = new_text.replace('\n', ' ')
    new_text = new_text.replace('\t', ' ')
    new_text = new_text.replace('"', "'")
    return f'"{new_text}"'


def make_invalid_varname_comment(varname: str):
    """Make a comment about a Stata varname being invalid."""
    return f'* Invalid STATA varname: {varname}'


def get_varname_comments(*args):
    """Make invalid Stata varname comments for many varnames."""
    comments = [make_invalid_varname_comment(i) for i in args if not
                is_valid_stata_varname(i)]
    return comments
