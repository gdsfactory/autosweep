import pathlib

import new_stuff

import autosweep
from autosweep.utils import registrar


def test_instr() -> None:
    registrar.register_classes(new_stuff)
    autosweep.init_logger()

    dirpath = pathlib.Path(__file__).parent.parent.absolute()
    station_cfg = autosweep.StationConfig.read_json(
        path=dirpath / "test_exec" / "station_config.json"
    )

    with autosweep.InstrumentManager(station_config=station_cfg) as i:
        i.load_instruments(instr_names="all")

    print(station_cfg.instruments)
    print(station_cfg.station_config)


if __name__ == "__main__":
    test_instr()
