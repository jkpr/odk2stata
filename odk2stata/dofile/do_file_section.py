from abc import ABC, abstractmethod

from ..dataset.column import Column
from ..dataset.dataset_collection import DatasetCollection


class DoFileSection(ABC):

    SOURCE_BRIEFCASE = 'briefcase'
    SOURCE_AGGREGATE = 'aggregate'
    SOURCE_NO_GROUPS = 'no_groups'
    ALLOWED_SOURCES = (SOURCE_BRIEFCASE, SOURCE_AGGREGATE, SOURCE_NO_GROUPS)

    DEFAULT_FIRST_LABEL = 'first_label'
    DEFAULT_EXTRA_LABEL = 'o2s_label'

    BASE_DEFAULT_SETTINGS = {
        'skip': False,
        'omit': False,
        'dataset_source': SOURCE_BRIEFCASE,
        'which_label': DEFAULT_FIRST_LABEL,
        'extra_label': DEFAULT_EXTRA_LABEL,
    }

    @property
    @abstractmethod
    def DEFAULT_SETTINGS(self):
        return {}

    def __init__(self, dataset_collection: DatasetCollection,
                 settings: dict = None, populate: bool = False):
        self.dataset_collection = dataset_collection
        self.settings = dict(self.BASE_DEFAULT_SETTINGS)
        self.settings.update(self.DEFAULT_SETTINGS)
        if settings:
            self.settings.update(settings)
        if populate:
            self.populate()

    @abstractmethod
    def populate(self):
        pass

    @abstractmethod
    def analyze_column(self, column: Column):
        pass

    @abstractmethod
    def do_file_iter(self):
        pass

    def initialize_settings(self, settings: dict, populate: bool = False):
        if settings:
            self.settings = dict(self.BASE_DEFAULT_SETTINGS)
            self.settings.update(self.DEFAULT_SETTINGS)
            self.settings.update(settings)
            if populate:
                self.populate()

    def update_settings(self, settings: dict, populate: bool = False):
        if settings:
            self.settings.update(settings)
            new_settings = dict(self.settings)
            self.initialize_settings(new_settings, populate)

    @property
    def skip(self):
        return self.settings['skip']

    @property
    def omit(self):
        return self.settings['omit']

    @property
    def dataset_source(self):
        result = self.settings['dataset_source']
        if result not in self.ALLOWED_SOURCES:
            methods = (f'"{i}"' for i in self.ALLOWED_SOURCES)
            methods = ', '.join(methods)
            msg = ('Under default section, "dataset_source" '
                   f'is set to {result}. Please update to be one of {methods}.')
            raise ValueError(msg)
        return result

    @property
    def which_label(self):
        return self.settings['which_label']

    @property
    def extra_label(self):
        return self.settings['extra_label']


