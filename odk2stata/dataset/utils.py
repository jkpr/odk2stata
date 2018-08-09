"""A collection of useful dataset-related functions."""
from enum import Enum
import string
from typing import List


class DatasetSource(Enum):
    """An enumeration of possible dataset sources."""
    BRIEFCASE = 1
    AGGREGATE = 2
    NO_GROUPS = 3

    @classmethod
    def from_string(cls, input: str):
        """Convert a string to enum."""
        if input.lower() == 'briefcase':
            return cls.BRIEFCASE
        elif input.lower() == 'aggregate':
            return cls.AGGREGATE
        elif input.lower() == 'no_groups':
            return cls.NO_GROUPS
        else:
            raise ValueError(input)


def get_column_name(row_name: str, ancestors: List[str],
                    dataset_source: DatasetSource) -> str:
    """Get the column name based on the node hierarchy.

    Args:
        row_name: The name defined in XLSForm.
        ancestors: The names of node ancestors, if any. These are the
            enclosing repeats and begin groups.
        dataset_source: The kind of dataset
    """
    if not isinstance(row_name, str):
        msg = (f'Parameter "row_name" must be of type "str". Got '
               f'{type(row_name)} instead')
        raise TypeError(msg)
    chunks = [*ancestors, row_name]
    if dataset_source == DatasetSource.BRIEFCASE:
        return '-'.join(chunks)
    elif dataset_source == DatasetSource.AGGREGATE:
        return ':'.join(chunks)
    elif dataset_source == DatasetSource.NO_GROUPS:
        return row_name
    else:
        msg = (f'Dataset source "{dataset_source}" should be one of '
               f'{list(DatasetSource)}')
        raise ValueError(msg)


def strip_illegal_chars(text: str) -> str:
    """Remove illegal characters.

    This routine mimics the same behavior in ODK Briefcase when it
    names the resultant dataset file (the .csv output).

    Args:
        text: Input string

    Returns:
        A string with illegal characters removed.
    """
    whitespace_dict = {ord(i): ' ' for i in string.whitespace}
    punctuation_dict = {ord(i): '_' for i in string.punctuation}
    result = text.translate({**whitespace_dict, **punctuation_dict})
    return result
