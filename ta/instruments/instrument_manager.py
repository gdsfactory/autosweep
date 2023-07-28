import logging


class InstrumentManager:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close_instruments(self):
        pass