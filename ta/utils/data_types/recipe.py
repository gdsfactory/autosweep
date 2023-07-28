import logging
from typing import Iterable

from ta.utils.data_types import filereader
from ta.utils import typing_ext
from ta.utils import io


class Recipe(filereader.FileWRer):

    def __init__(self, recipe: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.recipe = recipe

    @classmethod
    def from_dict(cls, data: dict):
        return cls(recipe=data)

    @classmethod
    def read_json(cls, path: typing_ext.PathLike):
        data = io.read_json(path=path)
        return cls.from_dict(data=data)

    def __eq__(self, other):
        if isinstance(other, Recipe):
            return self.recipe == other.recipe
        else:
            return False

    def to_json(self, path: typing_ext.PathLike):
        io.write_json(data=self.recipe, path=path)

    def to_dict(self, **kwargs) -> dict:
        return self.recipe

    def tests(self) -> Iterable[tuple]:
        for test in self.recipe['tests']:
            yield tuple(test)
