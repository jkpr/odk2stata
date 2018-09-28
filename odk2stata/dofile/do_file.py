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
from .varname_manager import VarnameManager
from ..dataset.dataset import Dataset


class DoFile:

    def __init__(self, dataset: Dataset,
                 settings: SettingsManager = None):
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
        case_preserve = self.settings.get_case_preserve()
        merge_single_repeat = self.settings.get_merge_single_repeat()
        merge_append = self.settings.get_merge_append()
        if self.original_dataset.is_repeat_dataset():
            merge_single_repeat = False
        dataset = ImportedDataset(self.original_dataset, case_preserve,
                                  merge_single_repeat, merge_append)
        return dataset

    def update_settings(self, settings):
        pass

    def render(self) -> str:
        template = env.get_template('base.do')
        result = template.render(
            metadata=self.metadata,
            drop_column=self.drop_column,
            rename=self.rename,
            destring=self.destring,
            encode_select_one=self.encode_select_one,
            split_select_multiple=self.split_select_multiple,
            label_variable=self.label_variable,
        )
        return result

    def write_out(self, path: str):
        render = self.render()
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(render)
