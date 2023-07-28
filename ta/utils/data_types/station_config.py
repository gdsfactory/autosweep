from pathlib import Path
import logging

from ta.utils.data_types import filereader
from ta.utils import typing_ext
from ta.utils import io


class StationConfig(filereader.FileWRer):

    def __init__(self, station_config: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.station_config = station_config

        self.station_config['paths']['base'] = Path(self.station_config['paths']['base'])

    @classmethod
    def from_dict(cls, data):
        return cls(station_config=data)

    @property
    def data_path(self) -> Path:
        return self.station_config['paths']['base'] / self.station_config['paths']['data']

    def to_json(self, path: typing_ext.PathLike):
        io.write_json(data=self.to_dict(), path=path)

    def to_dict(self) -> dict:
        return self.station_config