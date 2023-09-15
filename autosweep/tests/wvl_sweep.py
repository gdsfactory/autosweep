import time
from typing import TYPE_CHECKING

from autosweep import sweep
from autosweep.tests.abs_test import AbsTest
from autosweep.utils import ta_math

if TYPE_CHECKING:
    from autosweep.instruments.instrument_manager import InstrumentManager


class WvlSweep(AbsTest):
    """
    A laser wavelength sweep which records optical powermeter data.

    """

    def run_acquire(
        self,
        instr_mgr: "InstrumentManager",
        wvl_start: float,
        wvl_stop: float,
        dwvl: float,
    ):
        """
        Sweeps a laser and returns readings from 2 optical powermeters.

        :param instr_mgr: An instrument manager with the appropriate instruments
        :type instr_mgr: autosweep.instruments.instrument_manager.InstrumentManager
        :param wvl_start: The starting wavelength of the sweep (nm)
        :type wvl_start: float
        :param wvl_stop: The last wavelength of the sweep (nm)
        :type wvl_stop: float
        :param dwvl: The spacing between wavelengths (nm)
        :type dwvl: float
        :return: None
        """
        lsr = instr_mgr.instrs["laser"]  # gets laser from instrument manager
        opm = instr_mgr.instrs[
            "opt_pm"
        ]  # gets optical power meter from instrument manager

        wvls = ta_math.get_grid(start=wvl_start, stop=wvl_stop, step=dwvl)

        opm.sense_power_range(0)
        lsr.output_channel_state(output=0, channel=0, state=True)  # turning laser on
        # should replace this with a triggered read
        p1 = []
        p2 = []

        for wvl in wvls:
            lsr.source_channel_wavelength(0, 0, f"{wvl}NM")
            time.sleep(0.1)
            p1.append(
                opm.initiate_channel_immediate(1, 1)
            )  # makes a reading on channel 1
            p2.append(
                opm.initiate_channel_immediate(1, 2)
            )  # makes a reading on channel 2

        lsr.output_channel_state(output=0, channel=0, state=False)  # turning laser off

        traces = {"wvl": wvls, "p1": p1, "p2": p2}
        attrs = {
            "wvl": ("Wavelength", "nm"),
            "p1": ("Power", "dBm"),
            "p2": ("Power", "dBm"),
        }

        s = sweep.Sweep(traces=traces, attrs=attrs)
        self.save_data(sweeps={"wvl": s}, metadata=None)

    def run_analysis(self, report_headings: list):
        """
        Plots laser sweep data

        :param report_headings: A collection of headings used in the HTML report
        :type report_headings: list
        :return: None
        """
        self.load_data()
        self.logger.info("Running the virtual analysis")

        iv = self.sweeps["wvl"]

        fig_hdlr = sweep.FigHandler()
        ax = fig_hdlr.ax
        for col, x, y in iv.itercols():
            ax.plot(x, y, label=col)

        ax.legend()
        labels = iv.get_axis_labels()
        ax.set_xlabel(labels["wvl"])
        ax.set_ylabel(labels["p1"])

        fig_hdlr.save_fig(path=self.save_path / "wvl.png")

        report_heading = report_headings[0]
        self.results.add_report_entry(report_heading=report_heading, fig_hdlr=fig_hdlr)
