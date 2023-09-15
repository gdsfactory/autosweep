from autosweep.instruments import abs_instr

# @register_instr
# class VirtualInstr(abs_instr.AbsInstrument):
#     pass


class NewInstr(abs_instr.AbsInstrument):
    def get_idn(self):
        self._idn = "NewInstr, v1.0.0"
        return self.idn

    def close(self):
        # there's no com object so close is done
        pass
