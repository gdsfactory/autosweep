from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ta.instruments.instrument_manager import InstrumentManager


class AbsTest(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        pass

    @abstractmethod
    def run_analysis(self):
        pass

