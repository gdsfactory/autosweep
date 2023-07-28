from pathlib import Path
import logging

from autosweep import *
from autosweep.utils import registrar
from autosweep.utils.generics import find_last_run

import new_test

init_logger()
registrar.register_classes(new_test)
logging.info("Basic Test Exec functionality:")

dut = DUTInfo(part_num=PN('abc-0345', 1), ser_num=SN('123456'))
recipe = Recipe.read_json(path=Path('recipe.json'))
station_cfg = StationConfig.read_json(path=Path('../station_config.json'))

with TestExec(dut_info=dut, recipe=recipe, station_config=station_cfg, reanalyze=False) as t:
    t.run_recipe()

logging.info("Re-running the analysis:")
last_run = find_last_run(path='data')
with TestExec(dut_info=dut, recipe=recipe, station_config=station_cfg, reanalyze=True, path=last_run) as t:
    t.run_recipe()