import logging

from ta.utils.data_types.metadata_classes import PN, SN


class DUTInfo:

    def __init__(self, part_num, ser_num, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

        if isinstance(part_num, PN):
            self.part_num_obj = part_num
        else:
            raise TypeError("The type of argument 'part_num' must be PN")

        if isinstance(ser_num, SN):
            self.ser_num_obj = ser_num
        else:
            raise TypeError("The type of argument 'ser_num' must be SN")

        self.attrs = kwargs

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: PN: {self.part_num}, SN: {self.ser_num}>"

    @property
    def part_num(self) -> str:
        return self.part_num_obj.part_num

    @property
    def ser_num(self) -> str:
        return self.ser_num_obj.ser_num