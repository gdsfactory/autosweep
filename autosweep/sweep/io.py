from autosweep.utils import typing_ext
from autosweep.utils import io
from autosweep.data_types import metadata as md
from autosweep.sweep import sweep_parser


def read_json(path: typing_ext.PathLike):
    """
    With raw data saved in JSON form, this function parses the data

    :param path: The path to the JSON file which contains the data
    :type path: str or pathlib.Path
    :return: Three items are returned. 1) A dictionary of the Sweep objects contained in the file. 2) A dictionary of
        the global metadata. 3) The DUTInfo instance contained in the the file
    """
    data = io.read_json(path=path)

    dut = md.DUTInfo.from_dict(data=data['dut_info'])

    sweeps = {
        n: sweep_parser.Sweep.from_dict(data=d)
        for n, d in data['sweeps'].items()
    }
    return sweeps, data['metadata'], dut


def to_json(sweeps: dict, path: typing_ext.PathLike, metadata: dict | None = None,
            dut_info: md.DUTInfo | None = None) -> None:
    """
    Converts a set of raw data to JSON format. Useful for saving raw data to file used in scripting but also as part of
    the TestExec tests.

    :param sweeps: a collection of sweeps to write to a JSON file
    :type sweeps: dict[str, Sweep]
    :param path: The filename and path to write to
    :type path: str or pathlib.Path
    :param metadata: Any additional file-wide metadata you want to include
    :type metadata: dict, optional
    :param dut_info: The DUT info for this dataset
    :type dut_info: autosweep.data_types.metadata.DUTInfo, optional
    :return: None
    """

    out = {'dut_info': dut_info if dut_info else {},
           'metadata': metadata if metadata else {},
           'sweeps': {name: sweep.to_dict() for name, sweep in sweeps.items()}}

    io.write_json(data=out, path=path)