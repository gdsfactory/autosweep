from ta.tests.virt_test import VirtualTest
from ta.base.logger import init_logger


init_logger()

a = VirtualTest()
a.run_test(instr_mgr=None)
a.run_analysis()