import configparser
import io

from ..destring import Destring
from ..metadata import Metadata
from ..do_file_section import DoFileSection
from ..drop_column import DropColumn
from ..encode_select_one import EncodeSelectOne
from ..label_variable import LabelVariable
from ..rename import Rename
from ..split_select_multiple import SplitSelectMultiple
from ...dataset.utils import DatasetSource


def stringify_value(value):
    if isinstance(value, DatasetSource):
        result = dataset_source_to_str(value)
    elif isinstance(value, list):
        result = '\n'.join(value)
    else:
        result = str(value)
    return result


def stringify_values(settings):
    result = {k: stringify_value(v) for k, v in settings.items()}
    return result


def str_to_list(value: str) -> list:
    if not value:
        return []
    split = value.split('\n')
    return split


def list_to_str(value: list) -> str:
    if not value:
        return ''
    result = '\n'.join(value)
    return result


def str_to_dataset_source(value: str) -> DatasetSource:
    result = DatasetSource.from_string(value)
    return result


def dataset_source_to_str(value: DatasetSource) -> str:
    result = value.name.lower()
    return result


STR_BOOL_TRUE = ['true', 'yes', 't', 'y', '1']


def destringify_value(value: str, pattern):
    if isinstance(pattern, DatasetSource):
        result = DatasetSource.from_string(value)
    elif isinstance(pattern, list):
        result = str_to_list(value)
    elif isinstance(pattern, bool):
        result = value.lower() in STR_BOOL_TRUE
    else:
        result = value
    return result


def destringify_values(settings: dict, pattern: dict, default: dict) -> dict:
    result = {}
    combined_pattern = {}
    combined_pattern.update(default)
    combined_pattern.update(pattern)
    for k, v in settings.items():
        pattern_value = combined_pattern.get(k)
        if pattern_value is not None:
            value = destringify_value(v, pattern_value)
            result[k] = value
        else:
            # Setting will not be used
            result[k] = v
    return result


class SettingsManager:
    # Knows about each of the sections
    # Can take an ini file and make a dictionary for each section
    # Can make output in ini format or JSON format
    # Can retrieve other settings in this folder

    def __init__(self, path=None):
        self.default = {}
        self.destring = {}
        self.drop_column = {}
        self.encode_select_one = {}
        self.label_variable = {}
        self.metadata = {}
        self.rename = {}
        self.split_select_multiple = {}
        if path:
            self.import_from_file(path)
        else:
            self.set_all_to_default()

    def set_all_to_empty(self):
        self.default = {}
        self.destring = {}
        self.drop_column = {}
        self.encode_select_one = {}
        self.label_variable = {}
        self.metadata = {}
        self.rename = {}
        self.split_select_multiple = {}

    def set_all_to_default(self):
        self.default = DoFileSection.BASE_DEFAULT_SETTINGS.copy()
        self.destring = Destring.DEFAULT_SETTINGS.copy()
        self.drop_column = DropColumn.DEFAULT_SETTINGS.copy()
        self.encode_select_one = EncodeSelectOne.DEFAULT_SETTINGS.copy()
        self.label_variable = LabelVariable.DEFAULT_SETTINGS.copy()
        self.metadata = Metadata.DEFAULT_SETTINGS.copy()
        self.rename = Rename.DEFAULT_SETTINGS.copy()
        self.split_select_multiple = SplitSelectMultiple.DEFAULT_SETTINGS.copy()

    def import_from_file(self, path):
        config = configparser.ConfigParser(interpolation=None)
        config.read(path)
        self.destring = destringify_values(
            config['destring'],
            Destring.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.drop_column = destringify_values(
            config['drop_column'],
            DropColumn.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.encode_select_one = destringify_values(
            config['encode_select_one'],
            EncodeSelectOne.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.label_variable = destringify_values(
            config['label_variable'],
            LabelVariable.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.metadata = destringify_values(
            config['metadata'],
            Metadata.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.rename = destringify_values(
            config['rename'],
            Rename.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )
        self.split_select_multiple = destringify_values(
            config['split_select_multiple'],
            SplitSelectMultiple.DEFAULT_SETTINGS,
            DoFileSection.BASE_DEFAULT_SETTINGS
        )

    def to_dict(self):
        result = {
            'destring': self.destring,
            'drop_column': self.drop_column,
            'encode_select_one': self.encode_select_one,
            'label_variable': self.label_variable,
            'metadata': self.metadata,
            'rename': self.rename,
            'split_select_multiple': self.split_select_multiple,
        }
        return result

    def get_case_preserve(self) -> bool:
        return self.metadata['case_preserve']

    def get_merge_single_repeat(self) -> bool:
        return self.metadata['merge_single_repeat']

    def get_merge_append(self) -> bool:
        return self.metadata['merge_append']

    @classmethod
    def generate_default_ini(cls, path=None):
        settings = cls()
        settings.set_all_to_default()
        config = configparser.ConfigParser(interpolation=None)
        config['DEFAULT'] = stringify_values(settings.default)
        config['destring'] = stringify_values(settings.destring)
        config['drop_column'] = stringify_values(settings.drop_column)
        config['encode_select_one'] = \
            stringify_values(settings.encode_select_one)
        config['label_variable'] = stringify_values(settings.label_variable)
        config['metadata'] = stringify_values(settings.metadata)
        config['rename'] = stringify_values(settings.rename)
        config['split_select_multiple'] = \
            stringify_values(settings.split_select_multiple)
        if path:
            with open(path, 'w') as fp:
                config.write(fp, space_around_delimiters=True)
        else:
            output = io.StringIO()
            config.write(output, space_around_delimiters=True)
            contents = output.getvalue()
            output.close()
            return contents


if __name__ == '__main__':
    # SettingsManager.generate_default_ini('/Users/jpringle/Desktop/default.ini')
    # print(SettingsManager.generate_default_ini())
    sm = SettingsManager()
    sm.import_from_file('/Users/jpringle/Desktop/default.ini')
    print(sm.to_dict())
