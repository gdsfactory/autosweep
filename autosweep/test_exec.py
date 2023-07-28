import logging
from pathlib import Path

from autosweep.exec_helpers import status_writer, reporter
from autosweep.data_types import recipe, metadata, station_config
from autosweep.instruments import instrument_manager
from autosweep.utils import typing_ext, registrar, io, logger


class TestExec:
    """
    The TestExec is used to execute a series of tests over a device. More specifically, it uses a recipe and a station
    configuration to run setup instruments, take and analyze data and produce reports.

    :param dut_info: The information related to the device-under-test
    :type dut_info: autosweep.data_types.metadata.DUTInfo
    :param recipe: A collection of tests with parameters to execute
    :type recipe: autosweep.data_types.recipe.Recipe
    :param station_config: A collection of instrument configurations specific to a certain instrument
    :type station_config: autosweep.data_types.station_config.StationConfig
    :param gen_archive: Generate a ZIP file at the end of the data collection and report generation
    :type gen_archive: bool, default False
    :param reanalyze: When 'True', it is possible to re-analyze previously acquired test data
    :type reanalyze: bool, default False
    :param path: When 'reanalyze=True', this argument points to the data folder where the run is
    :type path: str or pathlib.Path, optional
    """

    def __init__(self,
                 dut_info: 'metadata.DUTInfo',
                 recipe: 'recipe.Recipe',
                 station_config: 'station_config.StationConfig',
                 gen_archive: bool = False,
                 reanalyze: bool = False,
                 path: typing_ext.PathLike | None = None):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.dut_info = dut_info
        self.recipe = recipe
        self.station_config = station_config

        self.reanalyze = reanalyze
        self.gen_archive = gen_archive

        self.instr_mgr = None
        # self.test_classes = {VirtualTest.__name__: VirtualTest}

        self.test_classes = registrar.TEST_CLASSES

        self.timestamp = {'start': metadata.TimeStamp(),
                          'end': None}

        run_name = f'{self.dut_info.part_num}_{self.dut_info.ser_num}_{self.timestamp["start"]}'
        if self.reanalyze:
            self.run_path = Path(path)
        else:
            self.run_path = self.station_config.data_path / run_name

        # Holds the functions related to writing the satus files, the test results, and code to generate reports, these
        # functions/classes can be replaced when test_exec is inherited from to change the behavior.

        self.status_writer = status_writer.write_status
        self.test_results = reporter.ResultsHold()
        self.reports_generator = reporter.gen_reports

        # holds the test instances after each recipe step is done
        self.test_instances = {}

        # the folder to look for the HTML template
        self.html_path = Path(__file__).parent / 'exec_helpers' / 'html'

    def __enter__(self):
        self.run_path.mkdir(exist_ok=True)

        # Any calls made to the logger will not be recorded to file if they are made before calling init_logger()
        logger.init_logger(path=self.run_path / f'runlog_{self.timestamp["start"]}.txt')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.reanalyze:
            self.instr_mgr.close_instruments()

        self.timestamp['end'] = metadata.TimeStamp()

        status_fname = f'status_renalysis_{self.timestamp["start"]}.json' if self.reanalyze else 'status.json'
        self.status_writer(test_exec=self, path=self.run_path / status_fname)
        self.reports_generator(test_exec=self)

        if self.gen_archive:
            io.write_archive(src_path=self.run_path, dst_path=self.run_path.parent)

    def run_recipe(self) -> None:
        """
        Executes the entire recipe

        :return:
        """
        if not self.reanalyze:
            self.logger.info("Starting instrument manager")
            self.instr_mgr = instrument_manager.InstrumentManager(station_config=self.station_config)
            self.instr_mgr.load_instruments(instr_names=self.recipe.instruments)

        for name, params in self.recipe.tests():
            self.run_recipe_step(name=name, params=params)

        self.logger.info(f"::: Done ---+---+---+--->>")

    def run_recipe_step(self, name: str, params: dict) -> None:
        """
        Executes an individual recipe step.

        :param name: The name of the recipe step
        :type name: str
        :param params: The full set of test parameters for the recipe step
        :type params: dict
        :return:
        """
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
