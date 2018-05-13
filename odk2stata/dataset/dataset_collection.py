import string

from .dataset import Dataset
from ..odkform import OdkForm
from ..odkform.survey import SurveyRow


class DatasetCollection:

    def __init__(self, odkform: OdkForm, dataset_source: str = 'briefcase'):
        self.odkform = odkform
        self.dataset_source = dataset_source
        primary_filename = self.dataset_filename(odkform, dataset_source)
        self.primary = Dataset(primary_filename, dataset_source)
        # Right now, support multiple, but not nested repeats
        self.repeats = []
        datasets = [self.primary]
        for row in odkform.survey:
            if row.becomes_column():
                datasets[-1].add_survey_row(row)
            if row.is_begin_repeat():
                filename = self.dataset_filename(odkform, dataset_source,
                                                 begin_repeat=row)
                repeat_dataset = Dataset(filename, dataset_source,
                                         begin_repeat=row)
                datasets.append(repeat_dataset)
            elif row.is_end_repeat():
                self.repeats.append(datasets.pop())

    @classmethod
    def from_file(cls, path: str, dataset_source: str = 'briefcase'):
        odkform = OdkForm(path)
        return cls(odkform, dataset_source)

    @staticmethod
    def dataset_filename(odkform: OdkForm, dataset_source: str = 'briefcase',
                         begin_repeat: SurveyRow = None):
        form_title = odkform.settings.form_title
        filename_uncleaned = form_title
        if begin_repeat is not None:
            filename_uncleaned = f'{filename_uncleaned}_{begin_repeat.row_name}'
        if dataset_source == 'aggregate':
            filename_uncleaned = f'{filename_uncleaned}_results'
        filename = DatasetCollection.strip_illegal_chars(filename_uncleaned)
        full_filename = f'{filename}.csv'
        return full_filename

    @staticmethod
    def strip_illegal_chars(text):
        whitespace_dict = {ord(i): ' ' for i in string.whitespace}
        punctuation_dict = {ord(i): '_' for i in string.punctuation}
        result = text.translate({**whitespace_dict, **punctuation_dict})
        return result

    def __iter__(self):
        return DatasetIter(self)

    def __repr__(self):
        msg = (f'DatasetCollection({repr(self.odkform)}, '
               f'"{self.dataset_source}")')
        return msg


class DatasetIter:

    def __init__(self, dataset_collection: DatasetCollection):
        self.primary = dataset_collection.primary.column_iter()
        self.repeats = [i.column_iter() for i in dataset_collection.repeats]
        self.current = [self.primary]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            col = next(self.current[-1])
            if col.survey_row.is_begin_repeat():
                self.current.append(self.repeats.pop(0))
        except StopIteration:
            self.current.pop()
            if self.current:
                col = next(self.current[-1])
            else:
                raise
        return col
