from ta.instruments import abs_instr
from ta.utils.registrar import register_instr


# @register_instr
# class VirtualInstr(abs_instr.AbsInstrument):
#     pass

@register_instr
class NewInstr(abs_instr.AbsInstrument):

    def get_idn(self):
        self._idn = "NewInstr, v1.0.0"
        return self.idn
