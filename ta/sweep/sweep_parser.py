import logging
import numpy as np
from typing import Iterable


class Sweep:

    def __init__(self, traces: dict, attrs: dict | None = None, metadata: dict | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)

        # checks on input types and shapes
        if not isinstance(traces, dict):
            raise TypeError("The argument 'traces' must be a dict.")

        if len(traces) < 2:
            raise ValueError("There must be more than 1 trace of data to make a sweep.")

        self._attrs = {}
        if attrs:
            if attrs.keys() != traces.keys():
                raise ValueError("The keys of 'traces' and 'attrs' must match.")

            self._attrs = attrs

        # parsing data
        self._traces = {k: np.array(v) for k, v in traces.items()}

        t_keys = tuple(self._traces.keys())
        self._aliases = {'x': t_keys[0], 'y': t_keys[1]}
        self._aliases.update({f'y{ii}': k for ii, k in enumerate(t_keys[1:])})

        self._ranges = {}
        self._len = len(self['x'])
        self._col_num = len(self._traces)
        for k, v in self._traces.items():
            self._ranges[k] = (np.min(v), np.max(v))

            # double check that every column has the same length
            if len(v) != self._len:
                msg = f"Trace '{k}' does not have the same length as the x-trace. Every trace must have the same " \
                      f"length."
                raise ValueError(msg)

        self.metadata = metadata if metadata else {}

    @classmethod
    def from_dict(cls, data: dict):
        return Sweep(**data)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        msg = f"<{self.__module__}.{self.__class__.__name__}, " \
               f"x-col: {self.x_col}, y-cols: {self.y_cols}, len: {len(self)}>"
        return msg

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, item):
        return self._traces[self.get_trace_col(col=item)]

    @property
    def shape(self) -> tuple:
        return self._col_num, self._len

    @property
    def attrs(self) -> dict[str, tuple]:
        return self._attrs

    @property
    def ranges(self) -> dict[str, tuple]:
        return self._ranges

    @property
    def x_col(self) -> str:
        return self._aliases['x']

    @property
    def y_cols(self) -> tuple:
        return tuple(self._traces.keys())[1:]

    def itercols(self) -> Iterable[tuple[str, np.ndarray, np.ndarray]]:
        for y in self.y_cols:
            yield y, self['x'], self[y]

    def get_trace_col(self, col) -> str:
        if col in self._aliases:
            return self._aliases[col]
        elif col in self._traces:
            return col
        else:
            raise KeyError(f"The trace '{col}' does not exist")

    def to_dict(self) -> dict:
        return {'traces': self._traces, 'attrs': self.attrs, 'metadata': self.metadata}

    def get_axis_labels(self, use_generic_names: bool = False) -> dict[str, str]:
        labels = {}
        if not self.attrs:
            raise Exception("No axis labels without Sweep attributes")

        if use_generic_names:
            keys = dict(map(reversed, self._aliases.items()))

        for k, v in self.attrs.items():
            if use_generic_names:
                k = keys[k]

            labels[k] = f"{v[0]} ({v[1]})"

        return labels

    def change_unit(self, col: str, coeff: float, unit: str | None = None, desc: str | None = None):
        col = self.get_trace_col(col=col)
        self._traces[col] = coeff*self._traces[col]

        if self.attrs:
            if not unit:
                raise ValueError("The argument 'unit' must be defined for a Sweep with attrs")

            if desc:
                self._attrs[col] = (desc, unit)
            else:
                self._attrs[col] = (self._attrs[col][0], unit)
