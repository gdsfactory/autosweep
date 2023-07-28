import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ta.base.data_types.metadata_classes import TimeStamp
from ta.instruments.instrument_manager import InstrumentManager
from ta.base.registrar import TEST_CLASSES
from ta.tests.virt_test import VirtualTest

if TYPE_CHECKING:
    from ta.base.data_types.dut_info import DUTInfo
    from ta.base.data_types.recipe import Recipe


class TestExec:

    def __init__(self, dut_info: 'DUTInfo', recipe: 'Recipe', reanalyze: bool = False):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info
        self.recipe = recipe

        self.reanalyze = reanalyze
        if self.reanalyze:
            raise NotImplementedError

        self.instr_mgr = None
        # self.test_classes = {VirtualTest.__name__: VirtualTest}
        self.test_classes = TEST_CLASSES

        self.timestamp = TimeStamp()

        run_name = f'{self.dut_info.part_num}_{self.dut_info.ser_num}_{self.timestamp}'
        self.run_path = Path('data') / run_name

    def __enter__(self):
        self.logger.info("Entering")

        self.run_path.mkdir(exist_ok=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instr_mgr.close_instruments()

    def run_recipe(self):
        self.logger.info("Starting instrument manager")
        self.instr_mgr = InstrumentManager()

        for name, params in self.recipe.tests():
            self.run_recipe_step(name=name, params=params)

        self.logger.info(f"::: Done ---+---+---+--->>")

    def run_recipe_step(self, name: str, params: dict):
        test_class = params['class']
        self.logger.info(f"::: {name} - {test_class} ---+---+--->>")
        # create directory for each test
        test_path = self.run_path / name
        test_path.mkdir(exist_ok=True)

        test = self.test_classes[test_class](dut_info=self.dut_info, save_path=test_path)
        test.run_acquire(instr_mgr=self.instr_mgr, **params['acquire'])
        out = test.run_analysis(**params['analysis'])
