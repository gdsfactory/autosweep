import logging

from ta.base.logger import init_logger
from ta.base.data_types.recipe import Recipe
from ta.base.data_types.dut_info import DUTInfo
from ta.base.data_types.metadata_classes import PN, SN, TimeStamp


init_logger()

pn = PN(num='ABC-12345', rev='123')
logging.info(f"{pn = }")
logging.info(f"{pn.part_num}")
logging.info(f"{str(pn)}")

sn = SN(num='123-12314')
logging.info(f"{sn = }")
logging.info(f"{sn.ser_num}")
logging.info(f"{str(sn)}")

dut = DUTInfo(part_num=pn, ser_num=sn, a='b', c='d')
logging.info(f"{dut = }")
logging.info(f"{dut.ser_num}")
logging.info(f"{str(dut)}")

ts = TimeStamp()
logging.info(f"{ts = }")
logging.info(f"{ts}")
ts1 = TimeStamp(timestamp=ts)
logging.info(f"{ts1 = }")
logging.info(f"{ts1}")
assert ts1 == ts, "Timestamps should match"

r = Recipe.read_json('../recipe.json')
r.to_json('recipe_2.json')
for n, t in r.tests():
    logging.info(f"{n}: {t}")

r2 = Recipe.read_json('recipe_2.json')
assert r == r2, "Recipes should match"