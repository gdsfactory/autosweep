from abc import ABC, abstractmethod
import logging


class AbsInstrument:
    """
    The base class for every instrument that is managed by the instrument manager. Every instrument driver should derive
    from this base class.
    """

    _ta_instr = True

    def __init__(self, com):
        """

        :param com: An instance of an object which can send commands and receive data from the instrument
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.com = com
        self._idn = ""
        self.get_idn()

    @property
    def idn(self) -> str:
        """

        :return: The "*IDN?" string of the instrument or equivalent
        """
        return self._idn

    def get_idn(self) -> str:
        """
        Queries the instrument using "*IDN?" for it's identifying string

        :return: The "*IDN?" string of the instrument or equivalent
        """
        self._idn = self.com.query('*IDN?')
        return self.idn

    def close(self):
        """
        Closes the instrument's communication port. Can also be expanded to perform other functions at shutdown as well.
        The instrument manager will call this function for every instrument instance.

        :return:
        """
        self.com.close()
