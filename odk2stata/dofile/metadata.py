"""A module for handling metadata about XLSForm data and Stata."""
import datetime
import getpass
import os.path

from .imported_dataset import ImportedDataset
from ..__version__ import __version__


class Metadata:
    """A class to represent the metadata about data from XLSForms.

    Class attributes:
        DEFAULT_SETTINGS: The default settings for this section
    """

    DEFAULT_SETTINGS = {
        'author': '',
        'timestamp_format': '%Y-%m-%d, %H:%M:%S',
        'case_preserve': False,
        'merge_single_repeat': True,
        'merge_append': True,
        'odk2stata_version': __version__
    }

    def __init__(self, dataset: ImportedDataset, settings: dict = None):
        """Initialize this metadata section.

        Args:
            dataset: The dataset that is produced upon Stata import
            settings: A settings dictionary to update defaults
        """
        self.dataset = dataset
        self.settings = dict(self.DEFAULT_SETTINGS)
        if settings:
            self.settings.update(settings)
        self.odk2stata_version = __version__
        self.odk_source_file = self.dataset.get_odk_source_file()
        self.primary_base = self.get_primary_base()
        self.primary_csv = self.get_primary_csv()
        self.primary_dta = self.get_primary_dta()
        self.secondary_csv = self.get_secondary_csv()
        self.secondary_dta = self.get_secondary_dta()
        self.merge_key = self.get_merge_key()

    def initialize_settings(self, settings: dict):
        if settings:
            self.settings = dict(self.DEFAULT_SETTINGS)
            self.settings.update(settings)

    def update_settings(self, settings: dict):
        if settings:
            self.settings.update(settings)
            new_settings = dict(self.settings)
            self.initialize_settings(new_settings)

    def get_odk_source_file(self):
        full_file = self.dataset.get_odk_source_file()
        _, source_file = os.path.split(full_file)
        return source_file

    def get_primary_base(self):
        filename = self.dataset.primary.dataset_filename
        base, _ = os.path.splitext(filename)
        return base

    def get_primary_csv(self):
        return self.dataset.primary.dataset_filename

    def get_primary_dta(self):
        base = self.get_primary_base()
        filename_dta = f'{base}.dta'
        return filename_dta

    def get_secondary_csv(self):
        if not self.dataset.secondary:
            return None
        return self.dataset.secondary.dataset_filename

    def get_secondary_dta(self):
        if not self.dataset.secondary:
            return None
        csv_filename = self.dataset.secondary.dataset_filename
        path, _ = os.path.splitext(csv_filename)
        filename_dta = f'{path}.dta'
        return filename_dta

    def is_merged_dataset(self):
        return self.dataset.is_merged_dataset()

    def get_merge_key(self):
        if not self.dataset.secondary:
            return None
        merge_column = self.dataset.secondary.begin_repeat
        for var in self.dataset:
            if var.column is merge_column:
                return var.orig_varname

    @property
    def author(self):
        settings_author = self.settings['author']
        author = settings_author if settings_author else getpass.getuser()
        return author

    @property
    def date_created(self):
        now = datetime.datetime.now()
        timestamp = now.strftime(self.settings['timestamp_format'])
        return timestamp

    @property
    def case_preserve(self):
        return self.settings['case_preserve']

    @property
    def merge_single_repeat(self):
        return self.settings['merge_single_repeat']
