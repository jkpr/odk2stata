import datetime
import getpass
import os.path

from .. import __version__
from ..dataset.dataset_collection import DatasetCollection
from ..dataset.utils import DatasetSource


class Metadata:

    DEFAULT_SETTINGS = {
        'timestamp_format': '%Y-%m-%d, %H:%M:%S',
        'dataset_source': DatasetSource.BRIEFCASE,
        'case_preserve': True,
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

    @property
    def case_preserve(self):
        return self.settings['case_preserve']
