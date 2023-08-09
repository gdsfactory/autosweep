import pyvisa

from autosweep.instruments.coms import base_com


class VisaCOM(base_com.BaseCOM):

    def __init__(self, addrs: str):
        super().__init__()
        rm = pyvisa.ResourceManager()

        self.com = rm.open_resource(addrs)
        self.addrs = addrs


    def write(self, cmd: str) -> None:
        self.com.write(cmd)

    def read(self) -> str:
        return self.com.read()

    def query(self, cmd: str) -> None:
        return self.com.query(cmd)

    def close(self) -> None:
        self.com.close()
