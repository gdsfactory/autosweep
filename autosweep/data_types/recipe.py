import logging
from collections.abc import Iterable

from autosweep.data_types import filereader
from autosweep.utils import io, typing_ext


class Recipe(filereader.FileWRer):
    def __init__(self, recipe: dict):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.recipe = recipe

    @classmethod
    def from_dict(cls, data: dict):
        return cls(recipe=data)

    def __eq__(self, other):
        return self.recipe == other.recipe if isinstance(other, Recipe) else False

    @property
    def instruments(self) -> tuple[str]:
        """
        Returns the instruments needed to run this recipe.

        :return: The instrument instance names needed
        :rtype: tuple[str]
        """
        return tuple(self.recipe["instruments"])

    def to_json(self, path: typing_ext.PathLike):
        io.write_json(data=self.recipe, path=path)

    def to_dict(self, **kwargs) -> dict:
        return self.recipe

    def tests(self) -> Iterable[tuple]:
        """
        Used to iterate over tests.

        :yields: tuple[str, dict]
        """
        for test in self.recipe["tests"]:
            yield tuple(test)
