from pathlib import Path
import types
import logging

from autosweep.data_types import filereader
from autosweep.utils import typing_ext
from autosweep.utils import io
from autosweep.utils import generics


class StationConfig(filereader.FileWRer):
    """
    Contains the details of the station configuration, including where to save data and which instruments are present
    and how to connect to them.

    :param station_config: The station configuration
    :type station_config: dict
    """

    def __init__(self, station_config: dict):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        # returns a mappingproxytype so no inadvertent editing is possible
        self.station_config = generics.load_into_mappingproxytype(data=station_config)

        self.base_path = Path(self.station_config['paths']['base'])

    @classmethod
    def from_dict(cls, data):
        return cls(station_config=data)

    @property
    def data_path(self) -> Path:
        """
        The path where data will be saved

        :return: The path
        :rtype: pathlib.Path
        """
        return self.base_path / self.station_config['paths']['data']

    @property
    def instruments(self) -> types.MappingProxyType:
        """
        Details on all the instruments present in the station

        :return: The instrument details
        :rtype: types.MappingProxyType
        """
        return self.station_config['instruments']

    def to_json(self, path: typing_ext.PathLike):
        io.write_json(data=self.to_dict(), path=path)

    def to_dict(self) -> dict:
        return self.station_config