import logging

from ta.utils.params import logger_format, logger_level
from ta.utils.typing_ext import PathLike


def init_logger(path: PathLike | None = None) -> None:
    """
    Used to configure the logging package for use inside this package. Can be used with other scripts as well.

    :param path: The path to the logging output file to append messages to.
    :type path: str or pathlib.Path, optional
    :return: None
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(level=logger_level)

    handlers = [logging.StreamHandler()]
    if path:
        handlers.append(logging.FileHandler(path))

    root_logger.handlers = []
    for handler in handlers:
        formatter = logging.Formatter(logger_format)
        handler.setFormatter(formatter)
        handler.setLevel(logger_level)

        root_logger.addHandler(handler)
