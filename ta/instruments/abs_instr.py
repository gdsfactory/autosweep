from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING


class AbsInstrument:

    def __init__(self, com):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.com = com
        self._idn = ""
        self.get_idn()

    @property
    def idn(self) -> str:
        return self._idn

    def get_idn(self) -> str:
        self._idn = self.com.query('*IDN?')
        return self.idn
