from pathlib import Path
from abc import ABC, abstractmethod

from ta.utils.typing_ext import PathLike


class GeneralIOClass(ABC):

    @abstractmethod
    def to_dict(self, **kwargs) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass


class FileWRer(GeneralIOClass):

    @classmethod
    def read_json(cls, path: PathLike):
        pass

    @classmethod
    def from_dict(cls, data: dict):
        pass

    @property
    def filename(self) -> Path:
        return self.filename

    def to_json(self, path: PathLike):
        pass

    def to_dict(self, **kwargs) -> dict:
        return vars(self)


