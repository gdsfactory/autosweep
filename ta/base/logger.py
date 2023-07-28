import logging

from ta.base.params import logger_frmt, logger_lvl
from ta.base.typing_ext import PathLike


def init_logger(path: PathLike | None = None):

    handlers = [logging.StreamHandler()]
    if path:
        handlers.append(logging.FileHandler(path))

    logging.basicConfig(format=logger_frmt, level=logger_lvl, handlers=handlers)

