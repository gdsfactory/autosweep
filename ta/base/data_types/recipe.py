import logging
from typing import Iterable

from ta.base.typing_ext import PathLike
from ta.base.io import read_json, write_json


class Recipe:

    def __init__(self, recipe: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.recipe = recipe

    @classmethod
    def read_json(cls, path: PathLike):
        data = read_json(path=path)
        return cls(recipe=data)

    def __eq__(self, other):
        if isinstance(other, Recipe):
            return self.recipe == other.recipe
        else:
            return False

    def to_json(self, path: PathLike):
        write_json(data=self.recipe, path=path)

    def tests(self) -> Iterable[tuple]:
        for test in self.recipe['tests']:
            yield tuple(test)
