import orjson

from ta.base.typing_ext import Pathlike


def read_json(path: Pathlike) -> dict:
    """

    :param path:
    :return:
    """
    with open(path, 'r') as f:
        raw = f.read()

    data = orjson.loads(raw)
    return data


def write_json(data: dict, path: Pathlike) -> None:
    """

    :param data:
    :param path:
    :return:
    """
    json_data = orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY)
    with open(path, 'wb') as f:
        f.write(json_data)
