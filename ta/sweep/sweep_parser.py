import logging
import numpy as np


class Sweep:

    def __init__(self, traces: dict, attrs: dict | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)

        # checks on input types and shapes
        if not isinstance(traces, dict):
            raise TypeError("The argument 'traces' must be a dict")

        if len(traces) < 2:
            raise ValueError("There must be more than 1 trace of data to make a sweep")

        self._attrs = {}
        if attrs:
            if attrs.keys() != traces.keys():
                raise ValueError("The keys of 'traces' and 'attrs' must match")

            self._attrs = attrs

        # parsing data
        self._traces = {k: np.array(v) for k, v in traces.items()}

        t_keys = tuple(self._traces.keys())
        self._aliases = {'x': t_keys[0], 'y': t_keys[1]}
        self._aliases.update({f'y{ii}': k for ii, k in enumerate(t_keys[1:])})

        self._ranges = {}
        for k, v in self._traces.items():
            self._ranges[k] = (np.min(v), np.max(v))

    def __getitem__(self, item):
        k = self._aliases[item] if item in self._aliases else item
        if k in self._traces:
            return self._traces[k]
        else:
            raise KeyError(f"The trace '{item}' does not exist")

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
