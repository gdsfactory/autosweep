from ta.tests.abs_test import AbsTest
from typing import TYPE_CHECKING
import numpy as np

from ta.base.registrar import register_test
from ta.sweep.sweep_parser import Sweep
from ta.sweep.vis_utils import FigHandler
if TYPE_CHECKING:
    from pathlib import Path
    from ta.instruments.instrument_manager import InstrumentManager
    from ta.base.data_types.dut_info import DUTInfo


@register_test
class VirtualTest(AbsTest):

    def __init__(self, dut_info: 'DUTInfo', save_path: 'Path'):
        super().__init__(dut_info=dut_info, save_path=save_path)
        self.logger.info("Initializing the virtual test")

    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        self.logger.info("Running the virtual test")

        v = np.linspace(-1, 1, 21)

        traces = {'v': v, 'i0': v/10, 'i1': v/20}
        attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

        s = Sweep(traces=traces, attrs=attrs)

        self.save_data(sweeps={'iv': s}, metadata=None)

    def run_analysis(self):
        self.load_data()
        self.logger.info("Running the virtual analysis")

        iv = self.sweeps['iv']

        fig_hdlr = FigHandler()
        ax = fig_hdlr.ax
        for col, x, y in iv.itercols():
            ax.plot(x, y, label=col)

        ax.legend()
        labels = iv.get_axis_labels()
        ax.set_xlabel(labels['v'])
        ax.set_ylabel(labels['i0'])

        fig_hdlr.save_fig(path=self.save_path / 'iv.png')