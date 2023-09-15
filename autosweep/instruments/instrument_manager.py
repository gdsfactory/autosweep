import inspect
import logging

from autosweep.data_types import StationConfig
from autosweep.instruments import abs_instr
from autosweep.utils import registrar


class InstrumentManager:
    """
    The instrument manager is used by the TestExec to initialize instruments before passing them onto each test step.
    The manager can also be used independently as part of a script, usually within it's context manager.
    """

    def __init__(self, station_config: StationConfig):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.station_config = station_config

        self.instr_classes = registrar.INSTR_CLASSES

        self._instrs = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_instruments()

    @property
    def instrs(self) -> dict:
        return self._instrs

    def load_instrument(self, instr_name: str) -> abs_instr.AbsInstrument:
        """
        Initialize an instrument based on its instance name in the station configuration. If the instrument is already
        initialized, the reference to the instance is returned instead of generating a new one.

        :param instr_name: The instance name to initialize
        :type instr_name: str
        :return: The instrument instance
        :rtype: autosweep.instruments.abs_instr.AbsInstrument
        """
        if instr_name not in self.station_config.instruments:
            raise ValueError(f"{instr_name} is not an instrument in the station config")

        if instr_name in self._instrs:
            return self._instrs[instr_name]
        instr_params = dict(self.station_config.instruments[instr_name])

        obj = self.instr_classes[instr_params.pop("class")]
        self.logger.info(f"[{instr_name}] Initializing .....")

        sig = inspect.signature(obj)
        for par in instr_params:
            if par not in sig.parameters:
                msg = (
                    f"For the instrument instance name '{instr_name}', the key '{par}' is not defined and "
                    f"should be removed"
                )
                raise ValueError(msg)

        for par, val in sig.parameters.items():
            if par not in instr_params:
                if val.default == inspect.Signature.empty:
                    msg = (
                        f"For the instrument instance name '{instr_name}', a value for the key '{par}' must "
                        f"be defined"
                    )
                    raise ValueError(msg)

        instr = obj(**instr_params)
        self.logger.info(f"[{instr_name}] {instr.idn}")
        self._instrs[instr_name] = instr
        return instr

    def load_instruments(self, instr_names: list[str] | tuple[str]) -> None:
        """
        Initializes a set of instruments based on their config instance names.

        :param instr_names: The instance names to initialize
        :type instr_names: list[str] or tuple[str]
        :return: None
        """

        if isinstance(instr_names, str):
            if instr_names.lower() == "all":
                instr_names = self.station_config.instruments.keys()
            else:
                raise ValueError(f"instr_names value '{instr_names}' is not supported")
        elif any(n_ not in self.station_config.instruments for n_ in instr_names):
            raise ValueError("One of the instruments is not in the station config")

        for instr_name in instr_names:
            self.load_instrument(instr_name=instr_name)

    def close_instruments(self):
        """
        This function will safely close every open instrument

        :return:
        """
        for _name, instr in self._instrs.items():
            instr.close()
