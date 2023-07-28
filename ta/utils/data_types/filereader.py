from pathlib import Path
from abc import ABC, abstractmethod

from ta.utils import typing_ext
from ta.utils import io


class GeneralIOClass(ABC):
    """
    :TODO start here
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        raise NotImplementedError

    @abstractmethod
    def to_dict(self, **kwargs) -> dict:
        raise NotImplementedError


class FileWRer(GeneralIOClass):

    @classmethod
    def read_json(cls, path: typing_ext.PathLike):
        data = io.read_json(path=path)
        return cls.from_dict(data=data)

    @property
    def filename(self) -> Path:
        return self.filename

    def to_json(self, path: typing_ext.PathLike):
        raise NotImplementedError

    def to_dict(self, **kwargs) -> dict:
        return vars(self)


