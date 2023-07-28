from ta.tests.abs_test import AbsTest
from typing import TYPE_CHECKING
from time import sleep
import numpy as np

from ta import sweep
if TYPE_CHECKING:
    from pathlib import Path
    from ta.instruments.instrument_manager import InstrumentManager
    from ta.utils.exec_helpers.reporter import ResultsHold
    from ta.utils.data_types.metadata import DUTInfo


class VirtualTest(AbsTest):

    def __init__(self, dut_info: 'DUTInfo', results: 'ResultsHold', save_path: 'Path'):
        super().__init__(dut_info=dut_info, results=results, save_path=save_path)
        self.logger.info("Initializing the virtual test")

    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        self.logger.info("Running the virtual test")

        v = np.linspace(-1, 1, 21)

        traces = {'v': v, 'i0': v/10, 'i1': v/20}
        attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

        s = sweep.Sweep(traces=traces, attrs=attrs)
        sleep(2)

        self.save_data(sweeps={'iv': s}, metadata=None)

    def run_analysis(self, report_headings: list):
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

        report_heading = report_headings[0]
        info = {"a": "hello world"}
        self.results.add_spec(report_heading=report_heading, spec='resist_i0', unit='Ohm', value=10)
        self.results.add_spec(report_heading=report_heading, spec='resist_i1', unit='Ohm', value=20)
        self.results.add_report_entry(report_heading=report_heading, fig_hdlr=fig_hdlr, info=info)
