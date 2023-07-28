import zipfile

import orjson
import csv
import typing

from autosweep.utils import typing_ext


def json_serializer(obj: typing.Any) -> str | dict:
    """
    A serializer to use with orjson for specific package types.

    :param obj: The instance to serialize
    :type obj: typing.Any
    :return: The serialized version of the input
    :rtype: str | dict
    """

    # This is done here due to circular import issues
    from autosweep.data_types import metadata

    if isinstance(obj, metadata.DUTInfo):
        return obj.to_dict()
    if isinstance(obj, metadata.TimeStamp):
        return str(obj)

    raise TypeError(f"{type(obj)} is not serialized by json_serializer")


def read_json(path: typing_ext.PathLike) -> dict:
    """
    Uses orjson to parse a JSON file

    :param path: The path to a JSON file to read
    :type path: str or pathlib.Path
    :return: The contents of the JSON file
    :rtype: dict
    """
    with open(path, 'r') as f:
        raw = f.read()

    data = orjson.loads(raw)
    return data


def write_json(data: dict, path: typing_ext.PathLike) -> None:
    """
    Uses orjson to write a JSON file with 2-space indent, numpy serialization, and automatic handling of certain
    internal types.

    :param data: The data to write to the JSON file
    :type data: dict
    :param path: The path to the JSON file to create
    :type path: str or pathlib.Path
    :return: None
    """
    json_data = orjson.dumps(data, default=json_serializer, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY)
    with open(path, 'wb') as f:
        f.write(json_data)


def write_csv(data: list[dict], path: typing_ext.PathLike) -> None:
    """
    A helper function to write a CSV file, used specifically to create the output spec table.

    :param data: The specs to write to a file
    :type data: list[dict]
    :param path: The path to the CSV file to create
    :type path: str or pathlib.Path
    :return: None
    """
    with open(path, 'w') as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(rowdicts=data)


def write_archive(src_path: typing_ext.PathLike, dst_path: typing_ext.PathLike) -> None:
    """
    Used to generate a ZIP file of a whole folder, specifically test data for archiving purposes. The generated ZIP file
    has the name of the folder to archive.

    :param src_path: The folder to archive
    :type src_path: str or pathlib.Path
    :param dst_path: The destination of the ZIP file.
    :type dst_path: str or pathlib.Path
    :return: None
    """

    dst_fn = dst_path / f'{src_path.name}.zip'

    with zipfile.ZipFile(dst_fn, mode='w') as arc:
        for fn in src_path.rglob('*'):
            arc.write(fn, arcname=fn.relative_to(src_path.parent))
