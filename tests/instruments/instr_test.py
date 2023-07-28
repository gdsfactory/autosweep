from pathlib import Path

import ta
from ta.utils import registrar

import new_stuff

registrar.register_classes(new_stuff)
ta.init_logger()

station_cfg = ta.StationConfig.read_json(path=Path('../station_config.json'))

with ta.InstrumentManager(station_config=station_cfg) as i:
    i.load_instruments(instr_names='all')

print(station_cfg.instruments)
print(station_cfg.station_config)
