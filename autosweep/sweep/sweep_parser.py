import logging
from collections.abc import Iterable
from typing import Any

import numpy as np

from autosweep.data_types import filereader
from autosweep.utils import ta_math


class Sweep(filereader.GeneralIOClass):
    """
    A class used to manipulate test data, usually taken as a sweep (IV, laser power meter, etc.). Simplifies handling
    metadta, units and import/export.

    :param traces: The collection of data from the sweep, in ch-name (key) - values (value) pairs.
    :type traces: dict
    :param attrs: The collection of trace attributes, with the same channel names as the traces
    :type attrs: dict, optional
    :param metadata: Any additional metadata specific to this sweep
    :type metadata: dict, optional
    """

    def __init__(
        self, traces: dict, attrs: dict | None = None, metadata: dict | None = None
    ):
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

            self._attrs = {k: tuple(attr) for k, attr in attrs.items()}

        # parsing data
        self._traces = {k: np.array(v) for k, v in traces.items()}

        t_keys = tuple(self._traces.keys())
        self._aliases = {"x": t_keys[0], "y": t_keys[1]} | {
            f"y{ii}": k for ii, k in enumerate(t_keys[1:])
        }
        self._ranges = {}
        self._len = len(self["x"])
        self._col_num = len(self._traces)
        for k, v in self._traces.items():
            self._ranges[k] = (np.min(v), np.max(v))

            # double check that every column has the same length
            if len(v) != self._len:
                msg = (
                    f"Trace '{k}' does not have the same length as the x-trace. Every trace must have the same "
                    f"length."
                )
                raise ValueError(msg)

        self.metadata = metadata if metadata else {}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Used to create a Sweep instance from a dict. Used primarily as part of file IO

        :param data: The data from a file
        :type data: dict
        :return: A sweep instance
        :rtype: autosweep.sweep.sweep_parser.Sweep
        """
        return Sweep(**data)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__module__}.{self.__class__.__name__}, x-col: {self.x_col}, y-cols: {self.y_cols}, len: {len(self)}>"

    def __len__(self) -> int:
        """
        The length of the traces contained in the Sweep instance.

        :return: The length
        :rtype: int
        """
        return self._len

    def __getitem__(self, item):
        return self._traces[self.get_trace_col(col=item)]

    @property
    def shape(self) -> tuple[int, int]:
        """
        The shape of traces.

        :return: The number of traces and the length of the traces
        :rtype: tuple[int, int]
        """
        return self._col_num, self._len

    @property
    def attrs(self) -> dict[str, tuple]:
        return self._attrs

    @property
    def ranges(self) -> dict[str, tuple]:
        """
        Accessor for the min and max values of each trace

        :return: The ranges of the trace data
        :rtype: dict[str, tuple]
        """
        return self._ranges

    @property
    def x_col(self) -> str:
        """
        Accessor for the name of the X column (first) trace data

        :return: The name of the first column of the trace data
        :rtype: str
        """
        return self._aliases["x"]

    @property
    def y_cols(self) -> tuple[str]:
        """
        Accessor for the name of the Y columns (second onward) trace data

        :return: The name of the Y columns of the trace data
        :rtype: tuple[str]
        """
        return tuple(self._traces.keys())[1:]

    def itercols(self) -> Iterable[tuple[str, np.ndarray, np.ndarray]]:
        """
        Iterate over traces as (y-name, x-data, y-data).

        :yield name: The name of the y-data
        :yield x_data: The array of x data
        :yield y_data: The array of y_data
        """

        for y in self.y_cols:
            yield y, self["x"], self[y]

    def get_trace_col(self, col: Any) -> str:
        """
        A helper function which checks the input column name against the trace names and their aliases.

        :raise KeyError: If col is neither an alias to nor the name of a trace, a KeyError is raised
        :param col: The input name to check
        :type col: Any
        :return: The trace name, not the alias
        :rtype: str
        """
        if col in self._aliases:
            return self._aliases[col]
        elif col in self._traces:
            return col
        else:
            raise KeyError(f"The trace '{col}' does not exist")

    def to_dict(self) -> dict:
        """
        Used to export all relevant parameters for re-creating the Sweep instance. Used in conjunction with from_dict()
        as part of file IO

        :return: The data needed to save to disk to recreate the instance
        :rtype: dict
        """
        return {"traces": self._traces, "attrs": self.attrs, "metadata": self.metadata}

    def get_axis_labels(self, use_generic_names: bool = False) -> dict[str, str]:
        """
        Returns axis labels based on attributes (attrs). If there are no attributes, an Exception is raised.

        :param use_generic_names: If True, the keys in the returned dictionary are the generic aliases, otherwise they
            are the actual trace names.
        :type use_generic_names: bool, default False
        :return: The axis labels generated from the attributes
        :rtype: dict[str, str]
        """
        labels = {}
        if not self.attrs:
            raise Exception("No axis labels without Sweep attributes")

        if use_generic_names:
            keys = dict(map(reversed, self._aliases.items()))

        for k, v in self.attrs.items():
            if use_generic_names:
                k = keys[k]

            labels[k] = f"{v[0]} ({v[1]})" if len(v) == 2 else v[0]
        return labels

    def change_unit(
        self, col: str, coeff: float, unit: str | None = None, desc: str | None = None
    ) -> None:
        """
        This method can change the scaling of a trace, it's unit, and its description. For example to change the
        a trace from 'V' to 'mV', the coeff is 1000 and the unit is 'mV'.

        :param col: The trace name to apply this operation to
        :type col: str
        :param coeff: The coefficient to apply to every element of the trace data
        :type coeff: float
        :param unit: The unit value to replace in the attrs entry for this column
        :type unit: str, optional
        :param desc: The description of the column in the attrs entry
        :type desc: str, optional
        :return: None
        """
        col = self.get_trace_col(col=col)
        self._traces[col] = coeff * self._traces[col]

        if self.attrs:
            if unit:
                self._attrs[col] = (desc, unit) if desc else (self._attrs[col][0], unit)
            else:
                raise ValueError(
                    "The argument 'unit' must be defined for a Sweep with attrs"
                )

    def filter_range(self, x_min: float, x_max: float):
        """
        Applies an operation to filter all trace data within the x-value range passed in.

        :param x_min: The new minimum value
        :type x_min: float
        :param x_max: The new maximum value
        :type x_min: float
        :return: A new Sweep instance with the same attrs and metadata as this Sweep, but with smaller trace data bound
            by the (x_min, x_max).
        """
        idx_min = ta_math.find_nearest_idx(array=self["x"], val=x_min)
        idx_max = ta_math.find_nearest_idx(array=self["x"], val=x_max)

        traces = {col: trace[idx_min:idx_max] for col, trace in self._traces.items()}
        return Sweep(
            traces=traces,
            attrs=self.attrs if self.attrs else None,
            metadata=self.metadata if self.metadata else None,
        )

    # def find_x_intercept(self, val: float, y_col: str):
    #     y = self[self.get_trace_col(col=y_col)]
    #     raise NotImplementedError
    #
    # def find_y_intercept(self, val: float, y_col: str):
    #     raise NotImplementedError
    # #
    # # def find_poly_fit(self, deg: int, y_col: str):
    # #     raise NotImplementedError
    # #
    # # def find_fft(self, y_col: str):
    # #     raise NotImplementedError
