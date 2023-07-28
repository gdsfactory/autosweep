from ta.instruments import abs_instr


class VirtualInstr(abs_instr.AbsInstrument):
    """
    A virtual instrument which can be used to develop and test code without the need for a physical instrument
    """

    def __init__(self, com: object | None = None):
        super().__init__(com=com)

    def get_idn(self) -> str:
        self._idn = "Virtual Instrument, v1.0.0, sn:1234"
        return self.idn
