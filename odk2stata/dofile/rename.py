from enum import Enum
import re

from .do_file_section import DoFileSection
from .drop_column import DropColumn
from .stata_utils import is_valid_stata_varname
from .stata_utils import VARNAME_CHARACTERS
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.column import Column
from ..error import RenameNotApplicableError, RenameNotSupportedError


class Rename(DoFileSection):

    DEFAULT_SETTINGS = {
        'direct_rename': [],
        'rename_types': [],
    }

    def __init__(self, dataset_collection: DatasetCollection,
                 drop_column: DropColumn, settings: dict = None,
                 populate: bool = False):
        self.rename_rules = []
        self.drop_column = drop_column
        super().__init__(dataset_collection, settings, populate)

    def populate(self):
        pass

    def analyze_column(self, column: Column):
        pass

    def do_file_iter(self):
        yield ''

    def get_varname(self, varname: str) -> str:
        """Apply rename rules to input varname.

        Args:
            varname: A STATA varname

        Returns:
            The varname that would be found in the dataset after
            applying the renaming in this object.
        """
        # TODO: Fix this. It is a stub
        return varname


    @property
    def direct_rename(self):
        result = self.settings['direct_rename']
        return result

    @property
    def rename_types(self):
        result = self.settings['rename_types']
        return result

    def __repr__(self):
        return f'<Rename, size: {len(self.rename_rules)}>'


class RenameRule:
    # A rule has the old and the new parts
    # The old and new parts get parsed

    SPECIAL_CHARS = '*?#.='

    def __init__(self, old: str, new: str):
        self.old = old
        self.old_parsed = RenameParser(self.old)
        self.new = new
        self.new_parsed = RenameParser(self.new)

    def affects(self, varname: str) -> bool:
        match = re.match(self.old_parsed.regex, varname)
        return bool(match)

    def apply(self, varname: str) -> str:
        if not self.affects(varname):
            raise RenameNotApplicableError(repr(self), varname)
        match = re.match(self.old_parsed.regex, varname)
        matches = list(zip(match.groups(), self.old_parsed))
        new_chunks = []
        for token in self.new_parsed:
            if token.type == RenameType.DIRECT:
                new_chunks.append(token.string())
            elif token.type == RenameType.ASTERISK:
                found = -1
                for i, item in enumerate(matches):
                    found = i
                    matched, token = item
                    if token.type == RenameType.ASTERISK:
                        result = matched
                        new_chunks.append(result)
                        break
                if found >= 0:
                    matches.pop(found)
        return ''.join(new_chunks)

    def direct_rename(self, varname: str) -> str:
        old_is_varname = self.is_stata_varname(self.old)
        new_is_varname = self.is_stata_varname(self.new)
        if varname == self.old and old_is_varname and new_is_varname:
            return self.new
        else:
            raise RenameNotApplicableError(repr(self), varname)

    @staticmethod
    def has_special_char(name: str) -> bool:
        has = any(char in name for char in RenameRule.SPECIAL_CHARS)
        return has

    @staticmethod
    def is_stata_varname(name: str) -> bool:
        return is_valid_stata_varname(name)

    def __repr__(self):
        return f'Rename("{self.old}", "{self.new}")'


class RenameParser:

    ASTERISK_REGEX = '([a-zA-Z0-9_]*)'

    def __init__(self, name: str):
        # Make tokens out of everything that matches
        # Match those tokens to the result (both should be the same length)
        self.name = name
        self.tokens = []
        current_token = RenameToken()
        for char in name:
            if current_token.is_compatible(char):
                current_token.add(char)
            else:
                self.tokens.append(current_token)
                current_token = RenameToken(char)
        self.tokens.append(current_token)
        self.regex = self.generate_regex()

    def generate_regex(self):
        regex_chunks = []
        for token in self.tokens:
            if token.type == RenameType.DIRECT:
                direct_match = f'({token.string()})'
                regex_chunks.append(direct_match)
            elif token.type == RenameType.ASTERISK:
                regex_chunks.append(self.ASTERISK_REGEX)
            else:
                raise NotImplementedError()
        return ''.join(regex_chunks)

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __repr__(self):
        return f'<RenameParser("{self.name}"), size: {len(self.tokens)}>'


class RenameToken:

    def __init__(self, first_char: str = None):
        self.chars = []
        self.type = None
        if first_char:
            self.chars.append(first_char)
            self.set_type(first_char)

    def string(self):
        return ''.join(self.chars)

    def is_empty(self):
        return len(self.chars) == 0

    def type_not_set(self):
        return self.type is None

    def is_compatible(self, char):
        if self.is_empty():
            return True
        elif self.type == RenameType.DIRECT:
            return char in VARNAME_CHARACTERS
        elif self.type == RenameType.ASTERISK:
            return False
        else:
            return NotImplementedError(char)

    def add(self, char):
        self.chars.append(char)
        if self.type_not_set():
            self.set_type(char)

    def set_type(self, char):
        if char == '*':
            self.type = RenameType.ASTERISK
        # elif char == '.':
        #     self.type = RenameType.PERIOD
        # elif char == '=':
        #     self.type = RenameType.EQUALS
        # elif char == '#':
        #     self.type = RenameType.OCTOTHORPE
        elif char in VARNAME_CHARACTERS:
            self.type = RenameType.DIRECT
        else:
            raise RenameNotSupportedError(char)

    def __repr__(self):
        return f'<RenameToken, {self.type}, "{self.string()}">'


class RenameType(Enum):
    """An enumeration of possible rename match types."""
    DIRECT = 1
    ASTERISK = 2
    PERIOD = 3
    EQUALS = 4
    OCTOTHORPE = 5
