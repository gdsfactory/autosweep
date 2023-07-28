from pathlib import Path
from abc import ABC, abstractmethod

from ta.base.typing_ext import Pathlike


class FileWRerBaseClass(ABC):

    @property
    @abstractmethod
    def filename(self) -> Path:
        pass

    @abstractmethod
    def to_dict(self, **kwargs) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass


class FileWRer(FileWRerBaseClass):

    filename = None

    @classmethod
    def read_json(cls, path: Pathlike):
        pass

    @property
    def filename(self) -> Path:
        return self.filename

    def write_json(self, path: Pathlike):
        pass

    def to_dict(self, **kwargs) -> dict:
        return vars(self)

    def from_dict(cls, data):
        pass

