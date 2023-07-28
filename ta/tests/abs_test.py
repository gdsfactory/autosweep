from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

from ta.utils.data_types.metadata import DUTInfo
from ta import sweep

if TYPE_CHECKING:
    from pathlib import Path
    from ta.instruments.instrument_manager import InstrumentManager


class AbsTest(ABC):

    def __init__(self, dut_info: 'DUTInfo', save_path: 'Path'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info

        self.instrument_manager = None

        self.save_path = save_path
        self.raw_data_fname = 'raw_data.json'

        self._raw_data = False
        self.metadata = None
        self.sweeps = None

    @abstractmethod
    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        raise NotImplementedError

    def save_data(self, sweeps: dict | None = None, metadata: dict | None = None):
        self.sweeps = sweeps
        self.metadata = metadata if metadata else {}

        sweep.io.to_json(sweeps=self.sweeps, metadata=self.metadata, dut_info=self.dut_info,
                         path=self.save_path / self.raw_data_fname)

        self._raw_data = True

    def load_data(self):
        # no point reading in data if it's already in memory
        if not self._raw_data:
            self.sweeps, self.metadata, _ = sweep.io.read_json(path=self.save_path / self.raw_data_fname)

    @abstractmethod
    def run_analysis(self):
        pass

