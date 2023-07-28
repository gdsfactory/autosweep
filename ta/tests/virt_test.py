from ta.tests.abs_test import AbsTest
from typing import TYPE_CHECKING
from time import sleep
import numpy as np


from ta.utils import registrar
from ta import sweep
if TYPE_CHECKING:
    from pathlib import Path
    from ta.instruments.instrument_manager import InstrumentManager
    from ta.utils.data_types.metadata import DUTInfo


@registrar.register_test
class VirtualTest(AbsTest):

    def __init__(self, dut_info: 'DUTInfo', save_path: 'Path'):
        super().__init__(dut_info=dut_info, save_path=save_path)
        self.logger.info("Initializing the virtual test")

    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        self.logger.info("Running the virtual test")

        v = np.linspace(-1, 1, 21)

        traces = {'v': v, 'i0': v/10, 'i1': v/20}
        attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

        s = sweep.Sweep(traces=traces, attrs=attrs)
        sleep(2)

        self.save_data(sweeps={'iv': s}, metadata=None)

    def run_analysis(self):
        self.load_data()
        self.logger.info("Running the virtual analysis")

        iv = self.sweeps['iv']

        fig_hdlr = sweep.FigHandler()
        ax = fig_hdlr.ax
        for col, x, y in iv.itercols():
            ax.plot(x, y, label=col)

        ax.legend()
        labels = iv.get_axis_labels()
        ax.set_xlabel(labels['v'])
        ax.set_ylabel(labels['i0'])

        fig_hdlr.save_fig(path=self.save_path / 'iv.png')