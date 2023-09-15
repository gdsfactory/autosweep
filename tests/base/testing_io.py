import logging

from autosweep.utils.io import read_json, write_json
from autosweep.utils.logger import init_logger


def test_io() -> None:
    # init_logger(path='testing.txt')
    init_logger()
    data = {"hello": {"1": "a", "b": 2}, "world": "123"}
    filename = "temp.json"

    write_json(data=data, path=filename)
    data_in = read_json(path=filename)

    assert data == data_in, "The data written should be the data read back"
    logging.info("Passed")
