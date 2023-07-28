import logging
from ta.tests.virt_test import VirtualTest
from ta.utils.logger import init_logger

from ta.instruments.virt_instr import VirtualInstr

init_logger()
# hello world
v = VirtualInstr(com=None)
logging.info(f"Instr IDN: {v.idn}")

a = VirtualTest()
a.run_acquision(instr_mgr=None)
a.run_analysis()