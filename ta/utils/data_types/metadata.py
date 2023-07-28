import logging
from datetime import datetime

from ta.utils.params import datetime_frmt


class PN:

    def __init__(self, num: str | int, rev: str | int):
        self.num = num.upper() if isinstance(num, str) else num
        self.rev = rev.upper() if isinstance(rev, str) else rev

        self._num_full = f"{self.num}-R{self.rev}"

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.part_num}>"

    @property
    def part_num(self) -> str:
        return self._num_full


class SN:

    def __init__(self, num: str | int):
        self.num = num

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.ser_num}>"

    @property
    def ser_num(self) -> str:
        return self.num


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

    @classmethod
    def from_dict(cls, data: dict):
        pn_dict = data['part_num']
        sn_dict = data['ser_num']

        part_num = PN(num=pn_dict['num'], rev=pn_dict['rev'])
        ser_num = SN(num=sn_dict['num'])

        return DUTInfo(part_num=part_num, ser_num=ser_num, **data['attrs'])

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: PN: {self.part_num}, SN: {self.ser_num}>"

    @property
    def part_num(self) -> str:
        return self.part_num_obj.part_num

    @property
    def ser_num(self) -> str:
        return self.ser_num_obj.ser_num

    def to_dict(self) -> dict:
        out = {'part_num': self.part_num_obj.__dict__,
               'ser_num': self.ser_num_obj.__dict__,
               'attrs': self.attrs}

        return out


class TimeStamp:

    def __init__(self, timestamp: str | datetime | None = None):
        if timestamp:
            if isinstance(timestamp, TimeStamp):
                self.timestamp = timestamp.timestamp
            elif isinstance(timestamp, datetime):
                self.timestamp = timestamp
            else:
                self.timestamp = datetime.strptime(timestamp, datetime_frmt)
        else:
            self.timestamp = datetime.now()

        self.timestamp_str = self.timestamp.strftime(datetime_frmt)

    def __str__(self) -> str:
        return self.timestamp_str

    def __eq__(self, other):
        if isinstance(other, TimeStamp):
            return self.timestamp == other.timestamp
        else:
            return False
