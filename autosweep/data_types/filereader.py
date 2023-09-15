from abc import ABC, abstractmethod

from autosweep.utils import io, typing_ext


class GeneralIOClass(ABC):
    """
    A base class to inherit from if the class you're building inside AutoSweep needs to perform disk or disk-like IO.
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """
        A class method to generate a class instance from a dict

        :param data: The data to generate the instance
        :type data: dict
        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self, **kwargs: dict) -> dict:
        """
        Used to turn the instance into a dictionary.

        :param kwargs: Any optional arguments
        :type kwargs: dict
        :return: The instance contents
        :rtype: dict
        """
        raise NotImplementedError


class FileWRer(GeneralIOClass):
    """
    A class which classes that perform file read and writes inherit from.
    """

    def __init__(self):
        self.filename = None

    @classmethod
    def read_json(cls, path: typing_ext.PathLike):
        """
        Create a class instance from a JSON file

        :param path:
        :type path: str or pathlib.Path
        :return:
        """
        data = io.read_json(path=path)
        obj = cls.from_dict(data=data)
        obj.filename = path
        return obj

    def to_json(self, path: typing_ext.PathLike) -> None:
        """
        Write the contents of the object instance to JSON in such a way that the classinstance can be re-generated.

        :param path: The file to write to.
        :type path: str or pathlib.Path
        :return: None
        """
        raise NotImplementedError

    def to_dict(self, **kwargs) -> dict:
        return vars(self)
