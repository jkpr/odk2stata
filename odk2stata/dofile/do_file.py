import datetime
import getpass
import os.path

from .templates import env
from .destring import Destring
from .drop_column import DropColumn
from .encode_select_one import EncodeSelectOne
from .label_variable import LabelVariable
from .rename import Rename
from .split_select_multiple import SplitSelectMultiple
from .varname_manager import VarnameManager
from .. import __version__
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.utils import DatasetSource


class DoFile:

    def __init__(self, dataset_collection: DatasetCollection,
                 settings: dict = None):
        self.dataset_collection = dataset_collection
        self.settings = settings
        self.varname_manager = VarnameManager()
        metadata_settings = self.settings_section('metadata')
        self.metadata = MetaData(dataset_collection, metadata_settings)
        drop_column_settings = self.settings_section('drop column')
        self.drop_column = DropColumn(dataset_collection, drop_column_settings,
                                      populate=True)
        rename_settings = self.settings_section('rename')
        self.rename = Rename(dataset_collection, self.drop_column,
                             rename_settings)
        destring_settings = self.settings_section('destring')
        self.destring = Destring(dataset_collection, self.drop_column,
                                 self.rename, destring_settings, populate=True)
        encode_select_one_setings = self.settings_section('encode select one')
        self.encode_select_one = EncodeSelectOne(dataset_collection,
                                                 self.drop_column, self.rename,
                                                 self.varname_manager,
                                                 encode_select_one_setings,
                                                 populate=True)
        split_select_multiple_setings = self.settings_section(
            'split select multiple'
        )
        self.split_select_multiple = SplitSelectMultiple(
            dataset_collection, self.drop_column, self.rename,
            split_select_multiple_setings, populate=True
        )
        label_variable_setings = self.settings_section('label variable')
        self.label_variable = LabelVariable(
            dataset_collection, self.drop_column, self.rename,
            label_variable_setings, populate=True
        )

    def settings_section(self, section: str) -> dict:
        settings_section = {}
        if self.settings:
            settings_section = self.settings.get(section, {})
        return settings_section

    def update_settings(self, settings):
        pass

    @classmethod
    def from_file(cls, path: str, dataset_source: str = 'briefcase'):
        dataset_collection = DatasetCollection.from_file(path, dataset_source)
        return cls(dataset_collection)

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
        with open(path, encoding='utf-8') as file:
            file.write(render)


class MetaData:

    DEFAULT_SETTINGS = {
        'timestamp_format': '%Y-%m-%d, %H:%M:%S',
        'dataset_source': DatasetSource.BRIEFCASE
    }

    def __init__(self, dataset_collection: DatasetCollection, settings=None):
        self.dataset_collection = dataset_collection
        self.settings = dict(self.DEFAULT_SETTINGS)
        if settings:
            self.settings.update(settings)

        self.odk2stata_version = __version__
        self.author = self.get_author()
        self.filename_csv = self.get_filename_csv()
        self.filename_dta = self.get_filename_dta()

    def initialize_settings(self, settings: dict):
        if settings:
            self.settings = dict(self.DEFAULT_SETTINGS)
            self.settings.update(settings)
            self.author = self.get_author()
            self.filename_csv = self.get_filename_csv()
            self.filename_dta = self.get_filename_dta()

    def update_settings(self, settings: dict):
        if settings:
            self.settings.update(settings)
            new_settings = dict(self.settings)
            self.initialize_settings(new_settings)

    def get_author(self):
        return getpass.getuser()

    def get_filename_csv(self):
        return self.dataset_collection.primary.dataset_filename

    def get_filename_dta(self):
        primary_filename = self.dataset_collection.primary.dataset_filename
        path, _ = os.path.splitext(primary_filename)
        filename_dta = f'{path}.dta'
        return filename_dta

    @property
    def date_created(self):
        now = datetime.datetime.now()
        timestamp = now.strftime(self.settings['timestamp_format'])
        return timestamp
