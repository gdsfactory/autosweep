# TODO: Might want to rename this. there is an IO in utils as well
from ta.utils import typing_ext
from ta.utils import io
from ta.utils.data_types import metadata as md
from ta.sweep import sweep_parser


def read_json(path: typing_ext.PathLike):
    data = io.read_json(path=path)

    dut = md.DUTInfo.from_dict(data=data['dut_info'])

    sweeps = {}
    for n, d in data['sweeps'].items():
        sweeps[n] = sweep_parser.Sweep.from_dict(data=d)

    return sweeps, data['metadata'], dut


def to_json(sweeps: dict, path: typing_ext.PathLike, metadata: dict | None = None,
            dut_info: md.DUTInfo | None = None):

    out = {'dut_info': dut_info if dut_info else {},
           'metadata': metadata if metadata else {},
           'sweeps': {name: sweep.to_dict() for name, sweep in sweeps.items()}}

    io.write_json(data=out, path=path)