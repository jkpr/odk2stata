"""Module for the DoFile class."""
from .templates import env
from .destring import Destring
from .drop_column import DropColumn
from .encode_select_one import EncodeSelectOne
from .imported_dataset import ImportedDataset
from .label_variable import LabelVariable
from .metadata import Metadata
from .rename import Rename
from .settings import SettingsManager
from .split_select_multiple import SplitSelectMultiple
from ..dataset.dataset import Dataset


class DoFile:
    """A class to represent a Stata do file.

    A do file is determined by the source dataset and the settings that
    are applied to generate the do file.

    Instance attributes:
        settings: The settings for creating this do file. If input
            settings is None, then default settings are used
        original_dataset: A reference to the input dataset
        dataset: The imported dataset for Stata
        metadata: Metadata about the dataset and import
        drop_column: A do file section for dropping variables
        rename: A do file section for renaming variables
        destring: A do file section for destring-ing variables
        encode_select_one: A do file section for encoding select_one
            variables
        split_select_multiple: A do file section for splititng
            select_multiple variables
        label_variable: A do file section for labeling variables
    """

    def __init__(self, dataset: Dataset,
                 settings: SettingsManager = None):
        """Initialize a Stata do file.

        Args:
            dataset: A dataset representing source CSV
            settings: The settings for creating this do file
        """
        self.settings = settings if settings is not None else SettingsManager()
        self.original_dataset = dataset
        self.dataset = self.get_imported_dataset()

        metadata_settings = self.settings.metadata
        self.metadata = Metadata(self.dataset, metadata_settings)
        drop_column_settings = self.settings.drop_column
        self.drop_column = DropColumn(self.dataset, drop_column_settings,
                                      populate=True)
        rename_settings = self.settings.rename
        self.rename = Rename(self.dataset, rename_settings, populate=True)
        destring_settings = self.settings.destring
        self.destring = Destring(self.dataset, destring_settings, populate=True)
        encode_select_one_settings = self.settings.encode_select_one
        self.encode_select_one = EncodeSelectOne(
            self.dataset, encode_select_one_settings, populate=True
        )
        split_select_multiple_settings = self.settings.split_select_multiple
        self.split_select_multiple = SplitSelectMultiple(
            self.dataset, split_select_multiple_settings, populate=True
        )
        label_variable_settings = self.settings.label_variable
        self.label_variable = LabelVariable(
            self.dataset, label_variable_settings, populate=True
        )

    def get_imported_dataset(self) -> ImportedDataset:
        """Return an ImportedDataset instance based on the source data."""
        case_preserve = self.settings.get_case_preserve()
        merge_single_repeat = self.settings.get_merge_single_repeat()
        merge_append = self.settings.get_merge_append()
        if self.original_dataset.is_repeat_dataset():
            merge_single_repeat = False
        dataset = ImportedDataset(self.original_dataset, case_preserve,
                                  merge_single_repeat, merge_append)
        return dataset

    def render(self) -> str:
        """Write this do file.

        Returns:
            The entire do-file as a string
        """
        template = env.get_template('base.do')
        result = template.render(
            metadata=self.metadata,
            drop_column=self.drop_column,
            rename=self.rename,
            destring=self.destring,
            encode_select_one=self.encode_select_one,
            split_select_multiple=self.split_select_multiple,
            ssm_details=self.split_select_multiple.get_ssm_details(),
            label_variable=self.label_variable,
        )
        return result

    def write_out(self, path: str):
        """Write out the result of the `render` routine.

        Args:
            path: Path to where the result should be saved
        """
        render = self.render()
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(render)
