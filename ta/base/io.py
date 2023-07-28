import orjson

from ta.base.typing_ext import PathLike
import ta.base.data_types.dut_info
import ta.sweep.sweep_parser


def json_serializer(obj):
    if isinstance(obj, ta.base.data_types.dut_info.DUTInfo):
        return obj.part_num
    if isinstance(obj, ta.sweep.sweep_parser.Sweep):
        return obj._traces

    raise TypeError(f"{type(obj)} is not serialized by json_serializer")


def read_json(path: PathLike) -> dict:
    """

    :param path:
    :return:
    """
    with open(path, 'r') as f:
        raw = f.read()

    data = orjson.loads(raw)
    return data


def write_json(data: dict, path: PathLike) -> None:
    """

    :param data:
    :param path:
    :return:
    """
    json_data = orjson.dumps(data, default=json_serializer, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY)
    with open(path, 'wb') as f:
        f.write(json_data)
