from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

from ta.utils.data_types.metadata import DUTInfo
from ta import sweep

if TYPE_CHECKING:
    from pathlib import Path
    from ta.utils.exec_helpers.reporter import ResultsHold
    from ta.instruments.instrument_manager import InstrumentManager


class AbsTest(ABC):

    _ta_test = True

    def __init__(self, dut_info: 'DUTInfo', results: 'ResultsHold', save_path: 'Path'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info

        self.instrument_manager = None

        self.save_path = save_path
        self.raw_data_fname = 'raw_data.json'

        self._raw_data = False
        self.metadata = None
        self.sweeps = None

        self.results = results

    @abstractmethod
    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        raise NotImplementedError

    def save_data(self, sweeps: dict | None = None, metadata: dict | None = None):
        for key, s in sweeps.items():
            if not isinstance(key, str):
                msg = f"The 'sweep' key, '{key}' should be a str"
                raise TypeError(msg)

            if not isinstance(s, sweep.Sweep):
                msg = f"The 'sweep' value for key '{key}' should be a ta.sweep.Sweep class instance"
                raise TypeError(msg)

        self.sweeps = sweeps
        self.metadata = metadata if metadata else {}

        sweep.io.to_json(sweeps=self.sweeps, metadata=self.metadata, dut_info=self.dut_info,
                         path=self.save_path / self.raw_data_fname)

        self._raw_data = True

    @abstractmethod
    def run_analysis(self, report_headings: list):
        raise NotImplementedError

    def load_data(self):
        # no point reading in data if it's already in memory
        if not self._raw_data:
            self.sweeps, self.metadata, _ = sweep.io.read_json(path=self.save_path / self.raw_data_fname)