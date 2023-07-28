from pathlib import Path
import logging

from ta import *

init_logger()
logging.info("Basic Test Exec functionality:")

dut = DUTInfo(part_num=PN('abc-1234', 1), ser_num=SN('123456'))
recipe = Recipe.read_json(path=Path('../recipe.json'))

with TestExec(dut_info=dut, recipe=recipe, reanalyze=False, path='data/ABC-1234-R1_123456_20230611-170533') as t:
    t.run_recipe()