from typing import List


def get_column_name(row_name: str, ancestors: List[str],
                    dataset_source: str) -> str:
    if not isinstance(row_name, str):
        msg = (f'Parameter "row_name" must be of type "str". Got '
               f'{type(row_name)} instead')
        raise TypeError(msg)
    chunks = [*ancestors, row_name]
    if dataset_source == 'briefcase':
        return '-'.join(chunks)
    elif dataset_source == 'aggregate':
        return ':'.join(chunks)
    elif dataset_source == 'no_groups':
        return row_name
    else:
        msg = (f'Dataset source "{dataset_source}" should be one of '
               '"briefcase", "aggregate", or "no_groups"')
        raise ValueError(msg)
