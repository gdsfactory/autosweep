class BaseCOM:

    def __init__(self):
        pass

    def write(self, cmd) -> None:
        raise NotImplementedError

    def read(self) -> None:
        raise NotImplementedError

    def query(self) -> None:
        raise NotImplementedError