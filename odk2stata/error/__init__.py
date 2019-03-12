"""A module defining custom exceptions for the package.

Each subpackage has a base exception class.
"""


class OdkFormError(Exception):
    """The base exception class for the odkform subpackage."""


class MismatchedGroupOrRepeatError(OdkFormError):
    """An exception for parsing group or repeats."""


class LabelNotFoundError(OdkFormError):
    """An excpetion for determining the label for an XlsFormRow."""


class DatasetError(Exception):
    """The base exception class for the dataset subpackage."""


class DoFileError(Exception):
    """The base exception class for the dofile subpackage."""


class RenameNotApplicableError(Exception):
    """An exception when trying to apply a rename that doesn't apply."""


class RenameNotSupportedError(Exception):
    """An exception when trying to apply a rename that doesn't apply."""
