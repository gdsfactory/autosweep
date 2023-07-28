from ta.tests.abs_test import AbsTest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ta.instruments.instrument_manager import InstrumentManager


class VirtualTest(AbsTest):

    def __init__(self):
        super().__init__()
        self.logger.info("Initializing the virtual test")

    def run_test(self, instr_mgr: 'InstrumentManager'):
        self.logger.info("Running the virtual test")

    def run_analysis(self):
        self.logger.info("Running the virtual analysis")