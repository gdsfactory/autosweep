import logging


class InstrumentManager:
    """
    The instrument manager is used by the TestExec to initialize instruments before passing them onto each test step.
    The manager can also be used independently as part of a script, usually within it's context manager.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_instruments()

    def close_instruments(self):
        """
        This function will safely close every open instrument

        :return:
        """
        pass