import logging

from ta.tests.virt_test import VirtualTest
from ta.base.logger import init_logger

from ta.instruments.virt_instr import VirtualInstr

init_logger()

v = VirtualInstr(com=None)
logging.info(f"Instr IDN: {v.idn}")

a = VirtualTest()
a.run_test(instr_mgr=None)
a.run_analysis()