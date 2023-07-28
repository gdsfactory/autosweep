from ta.tests.abs_test import AbsTest
from typing import TYPE_CHECKING
import numpy as np

from ta.sweep.sweep_parser import Sweep
if TYPE_CHECKING:
    from ta.instruments.instrument_manager import InstrumentManager


class VirtualTest(AbsTest):

    def __init__(self):
        super().__init__()
        self.logger.info("Initializing the virtual test")

    def run_test(self, instr_mgr: 'InstrumentManager'):
        self.logger.info("Running the virtual test")

        v = np.linspace(-1, 1, 11)
        i0 = v / 10
        i1 = v / 20

        traces = {'v': v, 'i0': v/10, 'i1': v/20}
        attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

        s = Sweep(traces=traces, attrs=attrs)

    def run_analysis(self):
        self.logger.info("Running the virtual analysis")