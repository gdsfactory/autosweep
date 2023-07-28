from pathlib import Path

import autosweep
from autosweep.utils import registrar

import new_stuff

registrar.register_classes(new_stuff)
autosweep.init_logger()

station_cfg = autosweep.StationConfig.read_json(path=Path('../station_config.json'))

with autosweep.InstrumentManager(station_config=station_cfg) as i:
    i.load_instruments(instr_names='all')

print(station_cfg.instruments)
print(station_cfg.station_config)
