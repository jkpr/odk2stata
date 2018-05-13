from .do_file_section import DoFileSection
from .drop_column import DropColumn
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.column import Column


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


class RenameRule:

    def affects(self, varname: str) -> bool:
        pass

    def apply(self, varname: str) -> str:
        pass
