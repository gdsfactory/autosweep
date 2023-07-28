import logging
from typing import Generator

from ta.base.typing_ext import Pathlike
from ta.base.io import read_json, write_json


class Recipe:

    def __init__(self, recipe: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.recipe = recipe

    @classmethod
    def read_json(cls, path: Pathlike):
        data = read_json(path=path)
        return cls(recipe=data)

    def __eq__(self, other):
        if isinstance(other, Recipe):
            return self.recipe == other.recipe
        else:
            return False

    def to_json(self, path: Pathlike):
        write_json(data=self.recipe, path=path)

    def tests(self) -> None:
        for test in self.recipe['tests']:
            yield tuple(test)