from .templates import env
from .destring import Destring
from .drop_column import DropColumn
from .encode_select_one import EncodeSelectOne
from .label_variable import LabelVariable
from .metadata import Metadata
from .rename import Rename
from .settings import SettingsManager
from .split_select_multiple import SplitSelectMultiple
from .varname_manager import VarnameManager
from ..dataset.dataset_collection import DatasetCollection


class DoFile:

    def __init__(self, dataset_collection: DatasetCollection,
                 settings: SettingsManager = None):
        self.dataset_collection = dataset_collection
        self.settings = settings if settings is not None else SettingsManager()
        self.varname_manager = VarnameManager()
        metadata_settings = self.settings.metadata
        self.metadata = Metadata(dataset_collection, metadata_settings)
        drop_column_settings = self.settings.drop_column
        self.drop_column = DropColumn(dataset_collection, drop_column_settings,
                                      populate=True)
        rename_settings = self.settings.rename
        self.rename = Rename(dataset_collection, self.drop_column,
                             rename_settings)
        destring_settings = self.settings.destring
        self.destring = Destring(dataset_collection, self.drop_column,
                                 self.rename, destring_settings, populate=True)
        encode_select_one_setings = self.settings.encode_select_one
        self.encode_select_one = EncodeSelectOne(dataset_collection,
                                                 self.drop_column, self.rename,
                                                 self.varname_manager,
                                                 encode_select_one_setings,
                                                 populate=True)
        split_select_multiple_setings = self.settings.split_select_multiple
        self.split_select_multiple = SplitSelectMultiple(
            dataset_collection, self.drop_column, self.rename,
            split_select_multiple_setings, populate=True
        )
        label_variable_setings = self.settings.label_variable
        self.label_variable = LabelVariable(
            dataset_collection, self.drop_column, self.rename,
            label_variable_setings, populate=True
        )

    def update_settings(self, settings):
        pass

    @classmethod
    def from_file(cls, path: str, dataset_source: str = 'briefcase',
                  settings_path: str = None):
        dataset_collection = DatasetCollection.from_file(path, dataset_source)
        settings = SettingsManager(settings_path)
        return cls(dataset_collection, settings)

    def render(self) -> str:
        template = env.get_template('base.do')
        result = template.render(
            metadata=self.metadata,
            rename=self.rename,
            destring=self.destring,
            drop_column=self.drop_column,
            encode_select_one=self.encode_select_one,
            label_variable=self.label_variable,
            split_select_multiple=self.split_select_multiple,
        )
        return result

    def write_out(self, path: str):
        render = self.render()
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(render)
