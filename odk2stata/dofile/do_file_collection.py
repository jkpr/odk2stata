from .do_file import DoFile
from .settings import SettingsManager
from ..dataset import DatasetCollection


class DoFileCollection:
    """A class to represent do files coming from the same ODK file.

    The DoFileCollection class corresponds to the DatasetCollection
    class. Thus, for each Dataset in a DatasetCollection, a DoFile is
    created and managed in this class.

    One small difference is that if there is a single repeat group in
    the source dataset, then there is an option to merge them together
    and have one DoFile for both.
    """

    def __init__(self, dataset_collection: DatasetCollection,
                 settings: SettingsManager = None):
        self.dataset_collection = dataset_collection
        self.settings = settings if settings else SettingsManager()
        self.do_files = []

        merge_in_settings = self.settings.get_merge_single_repeat()
        dataset_can_merge = self.dataset_collection.can_merge_single_repeat()
        if merge_in_settings and dataset_can_merge:
            do_file = DoFile(dataset_collection.primary, settings)
            self.do_files.append(do_file)
        else:
            for dataset in dataset_collection.get_datasets():
                do_file = DoFile(dataset, settings)
                self.do_files.append(do_file)

    @classmethod
    def from_file(cls, path: str, dataset_source: str = 'briefcase',
                  settings_path: str = None):
        dataset_collection = DatasetCollection.from_file(path, dataset_source)
        settings = SettingsManager(settings_path)
        return cls(dataset_collection, settings)

    def render(self):
        rendered = (do_file.render() for do_file in self.do_files)
        joined_do = '\n'.join(rendered)
        return joined_do

    def write_out(self, path: str):
        with open(path, mode='w', encoding='utf-8') as file:
            for do_file in self.do_files:
                render = do_file.render()
                file.write(render)

    def write_out_singly(self, path_to_dir: str):
        pass


if __name__ == '__main__':
    pass
