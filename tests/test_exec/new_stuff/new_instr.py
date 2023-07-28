from ta.instruments import abs_instr
from ta.utils.registrar import register_instr


@register_instr
class NewInstr(abs_instr.AbsInstrument):
    pass