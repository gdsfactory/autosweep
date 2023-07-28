import logging
from typing import TYPE_CHECKING

from ta.instruments.instrument_manager import InstrumentManager
if TYPE_CHECKING:
    from ta.base.data_types.dut_info import DUTInfo
    from ta.base.data_types.recipe import Recipe


class TestExec:

    def __init__(self, dut_info: 'DUTInfo', recipe: 'Recipe'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info
        self.recipe = recipe

    def __enter__(self):
        self.logger.info("Entering")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run_recipe(self):
        self.logger.info("Starting instrument manager")
        self.instr_manager = InstrumentManager()

        for step in self.recipe:
            self.run_recipe_step()

    def run_recipe_step(self):
        pass

