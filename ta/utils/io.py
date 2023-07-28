import orjson

from ta.utils import typing_ext
from ta.utils.data_types import metadata
from ta.sweep import sweep_parser


def json_serializer(obj):
    if isinstance(obj, metadata.DUTInfo):
        return obj.to_dict()
    if isinstance(obj, metadata.TimeStamp):
        return str(obj)
    if isinstance(obj, sweep_parser.Sweep):
        return obj._traces

    raise TypeError(f"{type(obj)} is not serialized by json_serializer")


def read_json(path: typing_ext.PathLike) -> dict:
    """

    :param path:
    :return:
    """
    with open(path, 'r') as f:
        raw = f.read()

    data = orjson.loads(raw)
    return data


def write_json(data: dict, path: typing_ext.PathLike) -> None:
    """

    :param data:
    :param path:
    :return:
    """
    json_data = orjson.dumps(data, default=json_serializer, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY)
    with open(path, 'wb') as f:
        f.write(json_data)
