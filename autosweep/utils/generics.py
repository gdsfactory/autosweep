import types
from pathlib import Path

from autosweep.utils import io
from autosweep.utils import typing_ext
from autosweep.data_types import metadata


def find_last_run(path: typing_ext.PathLike) -> Path:
    """
    A helper function that finds the latest run in a collection of data runs

    :param path: The path to the folder that holds multiple data runs
    :type path: str or pathlib.Path
    :return: The path to the latest data run
    :rtype: pathlib.Path
    """
    timestamps = []
    runs = []

    for run in sorted(Path(path).glob('*')):
        if run.is_dir():
            status_path = run / 'status.json'
            if status_path.exists():
                status = io.read_json(path=status_path)
                if timestamp_strs := status.get('timestamp'):
                    ts = metadata.TimeStamp(timestamp=timestamp_strs['start'])
                    timestamps.append(ts)
                    runs.append(run)

    sort_idx = [ii for ii, ts in sorted(enumerate(timestamps), key=lambda x: x[1])]
    return runs[sort_idx[-1]]


def load_into_mappingproxytype(data: dict) -> types.MappingProxyType:
    """
    Takes data from a dict to a 'types.MappingProxyType', which is read-only.

    :param data: The data to convert
    :type data: dict
    :return: The data in a read-only mapping.
    :rtype: types.MappingProxyType
    """
    new_data = {}
    for key, val in data.items():
        if isinstance(val, dict):
            val = load_into_mappingproxytype(data=val)

        new_data[key] = val

    return types.MappingProxyType(new_data)