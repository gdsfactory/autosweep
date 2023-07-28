from typing import TYPE_CHECKING

from ta.utils.typing_ext import PathLike
from ta.utils import io

if TYPE_CHECKING:
    from ta.test_exec import TestExec


def write_status(test_exec: 'TestExec', path: PathLike):
    out = {'dut_info': test_exec.dut_info,
           'timestamp': test_exec.timestamp}

    io.write_json(data=out, path=path)