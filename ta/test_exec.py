import logging
from typing import TYPE_CHECKING

from ta.instruments.instrument_manager import InstrumentManager
from ta.tests.virt_test import VirtualTest
if TYPE_CHECKING:
    from ta.base.data_types.dut_info import DUTInfo
    from ta.base.data_types.recipe import Recipe


class TestExec:

    def __init__(self, dut_info: 'DUTInfo', recipe: 'Recipe'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info
        self.recipe = recipe

        self.instr_mgr = None
        self.test_classes = {VirtualTest.__name__: VirtualTest}

    def __enter__(self):
        self.logger.info("Entering")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instr_mgr.close_instruments()
        pass

    def run_recipe(self):
        self.logger.info("Starting instrument manager")
        self.instr_mgr = InstrumentManager()

        for name, params in self.recipe.tests():
            self.run_recipe_step(name=name, params=params)

    def run_recipe_step(self, name: str, params: dict):
        test = self.test_classes[params['class']]()
        test.run_acquire(instr_mgr=self.instr_mgr, **params['acquire'])
        out = test.run_analysis(**params['analysis'])

        from IPython import embed
        embed(colors='neutral')


