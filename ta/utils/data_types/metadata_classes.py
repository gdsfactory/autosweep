from datetime import datetime

from ta.utils.params import datetime_frmt


class PN:

    def __init__(self, num: str | int, rev: str | int):
        self.num = num
        self.rev = rev

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
