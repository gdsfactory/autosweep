from pathlib import Path

from ta import *

init_logger()

dut = DUTInfo(part_num=PN('abc-1234', 1), ser_num=SN('123456'))
recipe = Recipe.read_json(path=Path('../recipe.json'))

with TestExec(dut_info=dut, recipe=recipe) as t:
    t.run_recipe()