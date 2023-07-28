import logging
import inspect

from ta.utils import data_types
from ta.utils import registrar


class InstrumentManager:
    """
    The instrument manager is used by the TestExec to initialize instruments before passing them onto each test step.
    The manager can also be used independently as part of a script, usually within it's context manager.
    """

    def __init__(self, station_config: data_types.station_config.StationConfig):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.station_config = station_config

        self.instr_classes = registrar.INSTR_CLASSES

        self.instrs = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_instruments()

    def load_instrument(self, instr_name: str):
        if instr_name not in self.station_config.instruments:
            raise ValueError(f"{instr_name} is not an instrument in the station config")

        instr_params = dict(self.station_config.instruments[instr_name])

        obj = self.instr_classes[instr_params.pop('class')]
        self.logger.info(f"[{instr_name}] {obj}")

        sig = inspect.signature(obj)
        for par in instr_params:
            if par not in sig.parameters:
                msg = f"For the instrument instance name '{instr_name}', the key '{par}' is not defined and should be " \
                      f"removed"
                raise ValueError(msg)

        for par, val in sig.parameters.items():
            if val.default == inspect.Signature.empty:
                if par not in instr_params:
                    msg = f"For the instrument instance name '{instr_name}', a value for the key '{par}' must " \
                          f"be defined"
                    raise ValueError(msg)

    def load_instruments(self, instr_names):
        if isinstance(instr_names, str):
            if instr_names.lower() == 'all':
                instr_names = self.station_config.instruments.keys()
            else:
                raise ValueError(f"instr_names value '{instr_names}' is not supported")
        else:
            if not all((n_ in self.station_config.instruments for n_ in instr_names)):
                raise ValueError("One of the instruments is not in the station config")

        for instr_name in instr_names:
            self.load_instrument(instr_name=instr_name)

    def close_instruments(self):
        """
        This function will safely close every open instrument

        :return:
        """
        pass