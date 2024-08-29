import pyvisa

from autosweep.instruments.coms import base_com


class VisaCOM(base_com.BaseCOM):
    def __init__(self, addrs: str):
        super().__init__()
        rm = pyvisa.ResourceManager()
        """
        Raw TCP/IP, serial, etc need newline termination
        Provide some reasonable defaults
        Ex: DiCom uses raw TCP/IP not T&M protocol
        https://pyvisa.readthedocs.io/en/1.5-docs/instruments.html#sec-termchars
        """
        if addrs.endswith("SOCKET"):
            self.com = rm.open_resource(
                addrs, write_termination="\r", read_termination="\r"
            )
        else:
            self.com = rm.open_resource(
                addrs, write_termination="\n", read_termination="\n"
            )
        self.addrs = addrs

    def write(self, cmd: str) -> None:
        self.com.write(cmd)

    def read(self) -> str:
        return self.com.read()

    def query(self, cmd: str) -> None:
        return self.com.query(cmd)

    def close(self) -> None:
        self.com.close()
