class PN:

    def __init__(self, part_num: str | int, rev: str | int):
        pass

    @property
    def part_num(self) -> str:
        pass


class SN:

    def __init__(self, ser_num: str | int):
        pass

    @property
    def ser_num(self) -> str:
        pass


class DUT:

    def __init__(self, part_num, ser_num, **kwargs):
        pass

