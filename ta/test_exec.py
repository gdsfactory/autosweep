import logging
from pathlib import Path

from ta.utils import data_types
from ta.instruments import instrument_manager
from ta.utils import typing_ext
from ta.utils import registrar
from ta.utils.exec_helpers.status_writer import write_status
from ta.utils.exec_helpers import reporter
from ta.utils.logger import init_logger


class TestExec:

    def __init__(self,
                 dut_info: 'data_types.metadata.DUTInfo',
                 recipe: 'data_types.recipe.Recipe',
                 station_config: 'data_types.station_config.StationConfig',
                 reanalyze: bool = False,
                 path: typing_ext.PathLike | None = None):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info
        self.recipe = recipe
        self.station_config = station_config

        self.reanalyze = reanalyze

        self.instr_mgr = None
        # self.test_classes = {VirtualTest.__name__: VirtualTest}

        self.test_classes = registrar.TEST_CLASSES

        self.timestamp = {'start': data_types.metadata.TimeStamp(),
                          'end': None}

        run_name = f'{self.dut_info.part_num}_{self.dut_info.ser_num}_{self.timestamp["start"]}'
        if self.reanalyze:
            self.run_path = Path(path)
        else:
            self.run_path = self.station_config.data_path / run_name

        self.status_writer = write_status
        self.test_results = reporter.ResultsHold()
        self.test_instances = {}
        self.reports_generator = reporter.gen_reports

    def __enter__(self):
        self.run_path.mkdir(exist_ok=True)

        # Any calls made to the logger will not be recorded to file if they are made before calling init_logger()
        init_logger(path=self.run_path / f'runlog_{self.timestamp["start"]}.txt')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.reanalyze:
            self.instr_mgr.close_instruments()

        self.timestamp['end'] = data_types.metadata.TimeStamp()

        status_fname = f'status_renalysis_{self.timestamp["start"]}.json' if self.reanalyze else 'status.json'
        self.status_writer(test_exec=self, path=self.run_path / status_fname)
        self.reports_generator(test_exec=self)

    def run_recipe(self):
        if not self.reanalyze:
            self.logger.info("Starting instrument manager")
            self.instr_mgr = instrument_manager.InstrumentManager(station_config=self.station_config)
            self.instr_mgr.load_instruments(instr_names=self.recipe.instruments)

        for name, params in self.recipe.tests():
            self.run_recipe_step(name=name, params=params)

        self.logger.info(f"::: Done ---+---+---+--->>")

    def run_recipe_step(self, name: str, params: dict):
        test_class = params['class']
        self.logger.info(f"::: {name} - {test_class} ---+---+--->>")
        # create directory for each test
        test_path = self.run_path / name
        test_path.mkdir(exist_ok=True)

        test_instance = self.test_classes[test_class](dut_info=self.dut_info, results=self.test_results,
                                                      save_path=test_path)

        # Don't acquire data if doing re-analysis
        if not self.reanalyze:
            test_instance.run_acquire(instr_mgr=self.instr_mgr, **params['acquire'])

        test_instance.run_analysis(**params['analysis'])
        self.test_results.validate()
        self.test_instances[name] = test_instance
