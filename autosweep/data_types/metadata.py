import logging
import functools
from datetime import datetime

from autosweep.utils.params import datetime_frmt


class MetaNum:
    """
    A MetaNum is any alphanumeric string or int that is used to represent a specific value with fixed formatting

    :param num: The value to hold
    :type num: str or int
    """

    def __init__(self, num: str | int):
        self.num = num.upper() if isinstance(num, str) else num

    def __str__(self) -> str:
        """
        :return: The string representation of this MetaNum
        :rtype: str
        """
        return f"<{self.__module__}.{self.__class__.__name__}: {self.num}>"

    @classmethod
    def from_dict(cls, data: dict):
        """
        A class method to generate a class instance from a dict

        :param data: The data to generate the instance
        :type data: dict
        """
        return cls(**data)

    def to_dict(self) -> dict:
        """
        Used to turn the instance into a dictionary.

        :return: The instance contents
        :rtype: dict
        """
        return self.__dict__


class PN(MetaNum):
    """
    The representation of a part number with a revision.

    :param num: The principle part of the part number
    :type num: str or int
    :param rev: The revision of the part number
    :type rev: str or int
    """

    def __init__(self, num: str | int, rev: str | int):
        super().__init__(num=num)

        self.rev = rev.upper() if isinstance(rev, str) else rev
        self._num_full = f"{self.num}-R{self.rev}"

    def __str__(self) -> str:
        return f"<{self.__module__}.{self.__class__.__name__}: {self.part_num}>"

    @property
    def part_num(self) -> str:
        """
        An accessor for the full part number

        :return: The full part number with revision
        :rtype: str
        """
        return self._num_full

    def to_dict(self) -> dict:
        return {'num': self.num, 'rev': self.rev}


class SN(MetaNum):
    """
    The representation of a serial number.

    :param num: The serial number
    :type num: str or int
    """

    @property
    def ser_num(self) -> str:
        """
        An accessor for the serial number

        :return: The serial number
        :rtype: str
        """
        return self.num


class DUTInfo:
    """
    DUTInfo stores the part number, the serial number, and any additional information relevant to the DUT.


    :param part_num: The DUT part number
    :type part_num: autosweep.data_types.metadata.PN
    :param ser_num: The DUT serial number
    :type ser_num: autosweep.data_types.metadata.SN
    :param kwargs: Any additional information
    :type kwargs: dict
    """

    def __init__(self, part_num: PN, ser_num: SN, **kwargs: dict):
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
        """
        A class method to generate a class instance from a dict

        :param data: The data to generate the instance
        :type data: dict
        """
        pn_dict = data['part_num']
        sn_dict = data['ser_num']

        part_num = PN(num=pn_dict['num'], rev=pn_dict['rev'])
        ser_num = SN(num=sn_dict['num'])

        return DUTInfo(part_num=part_num, ser_num=ser_num, **data['attrs'])

    def __str__(self) -> str:
        return f"<{self.__module__}.{self.__class__.__name__}: PN: {self.part_num}, SN: {self.ser_num}>"

    @property
    def part_num(self) -> str:
        """
        An accessor for the full part number

        :return: The part number
        :rtype: str
        """
        return self.part_num_obj.part_num

    @property
    def ser_num(self) -> str:
        """
        An accessor for the serial number

        :return: The serial number
        :rtype: str
        """
        return self.ser_num_obj.ser_num

    def to_dict(self) -> dict:
        """
        Used to turn the instance into a dictionary.

        :return: The instance contents
        :rtype: dict
        """

        return {
            'part_num': self.part_num_obj.to_dict(),
            'ser_num': self.ser_num_obj.to_dict(),
            'attrs': self.attrs,
        }


@functools.total_ordering
class TimeStamp:
    """
    A TimeStamp is a simple object based on python's datetime which is used to represent dates and times in a convinent
    way for AutoSweep.

    :param timestamp: The datetime to store, if nothing is specified, then the stored datetime is now.
    :type timestamp: str or datetime.datetime, optional
    """

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
        """
        An accessor to the standardized string representation of the datetime stored in this instance

        :return: The timestamp
        :rtype: str
        """
        return self.timestamp_str

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}: {self.timestamp_str}>"

    def __eq__(self, other):
        if isinstance(other, TimeStamp):
            return self.timestamp == other.timestamp
        else:
            return False

    def __gt__(self, other):
        if isinstance(other, TimeStamp):
            return self.timestamp > other.timestamp
        else:
            return False
