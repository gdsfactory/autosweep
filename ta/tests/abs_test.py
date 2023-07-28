from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

from ta.utils.io import write_json, read_json
from ta.utils.data_types.dut_info import DUTInfo

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

        self._raw_data = None
        self.metadata = None
        self.sweeps = None

    @abstractmethod
    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        pass

    def save_data(self, sweeps: dict | None = None, metadata: dict | None = None):

        out = {'dut_info': self.dut_info,
               'metadata': metadata if metadata else {},
               'sweeps': sweeps if sweeps else {}}

        write_json(data=out, path=self.save_path / self.raw_data_fname)

        self._raw_data = out

    def load_data(self):
        # no point reading in data if it's already in memory
        if not self._raw_data:
            self._raw_data = read_json(path=self.save_path / self.raw_data_fname)

        self.metadata = self._raw_data['metadata']
        self.sweeps = self._raw_data['sweeps']

    @abstractmethod
    def run_analysis(self):
        pass

