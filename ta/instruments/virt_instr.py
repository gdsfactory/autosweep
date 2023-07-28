import logging

from ta.instruments.abs_instr import AbsInstrument
from ta.utils import registrar


@registrar.register_instr
class VirtualInstr(AbsInstrument):

    def __init__(self, com: object | None = None):
        super().__init__(com=com)

    def get_idn(self) -> str:
        self._idn = "Virtual Instrument"
        return self.idn
