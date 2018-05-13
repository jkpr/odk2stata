"""A module defining custom exceptions for the package.

Each subpackage has a base exception class.
"""


class OdkFormError(Exception):
    """The base exception class for the odkform subpackage."""
    pass


class MismatchedGroupOrRepeatError(OdkFormError):
    """An exception for parsing group or repeats."""
    pass


class LabelNotFoundError(OdkFormError):
    """An excpetion for determining the label for an XlsFormRow."""
    pass


class DatasetError(Exception):
    """The base exception class for the dataset subpackage."""
    pass


class DoFileError(Exception):
    """The base exception class for the dofile subpackage."""
    pass
