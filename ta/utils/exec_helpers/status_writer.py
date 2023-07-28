from typing import TYPE_CHECKING

from ta.utils.typing_ext import PathLike
from ta.utils import io

if TYPE_CHECKING:
    from ta.test_exec import TestExec


def write_status(test_exec: 'TestExec', path: PathLike) -> None:
    """
    Used to write the status file

    :param test_exec: The test exec
    :type test_exec: ta.test_exec.TestExec
    :param path: The location to write the status file to
    :type path: str or pathlib.Path
    :return: None
    """
    out = {'dut_info': test_exec.dut_info,
           'timestamp': test_exec.timestamp}

    io.write_json(data=out, path=path)