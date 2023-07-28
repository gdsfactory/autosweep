from pathlib import Path
import logging

from autosweep.data_types import filereader
from autosweep.utils import typing_ext
from autosweep.utils import io
from autosweep.utils import generics


class StationConfig(filereader.FileWRer):

    def __init__(self, station_config: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.station_config = generics.load_into_mappingproxytype(data=station_config)
        # self.station_config = station_config

        self.base_path = Path(self.station_config['paths']['base'])

        # validate the station config, especially instrument side

    @classmethod
    def from_dict(cls, data):
        return cls(station_config=data)

    @property
    def data_path(self) -> Path:
        return self.base_path / self.station_config['paths']['data']

    @property
    def instruments(self):
        return self.station_config['instruments']

    def to_json(self, path: typing_ext.PathLike):
        io.write_json(data=self.to_dict(), path=path)

    def to_dict(self) -> dict:
        return self.station_config