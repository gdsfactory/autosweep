import numpy as np
from autosweep.utils import typing_ext


def find_nearest_idx(array: typing_ext.ListLike, val: float) -> int:
    """
    Find the nearest index of an array for a value

    :param array: The array to search
    :type array: np.ndarray or list or tuple
    :param val: The value to search for
    :type val: float
    :return: The closest matching index
    :rtype: int
    """
    return np.abs(array - val).argmin()


def find_3_idxs(array: typing_ext.ListLike, val: float) -> tuple[int, int] | tuple[int, int, int]:
    """
    Find the nearest 3 indices of an array for a value
    :param array: The array to search
    :type array: np.ndarray or list or tuple
    :param val: The value to search for
    :type val: float
    :return: The closest matching 2 or 3 indices
    :rtype: tuple[int, int] | tuple[int, int, int]
    """
    idx = find_nearest_idx(array=array, val=val)

    if idx == 0:
        return 0, 1
    elif idx == len(array) - 1:
        return idx-1, idx
    else:
        return idx-1, idx, idx+1


def get_grid(start: float, stop: float, step: float) -> np.ndarray:
    """
    Don't use np.arange for non-integer step sizes, use this instead. In cases where the step does not fit inside the
    interval, the result step is only approximate.

    :param start: The first value of the array
    :type start: float
    :param stop: The final value of the array
    :type stop: float
    :param step: The step size between elements in the array. Negative values are ignored.
    :type step: float
    :return: The array
    :rtype: np.ndarray
    """

    return np.linspace(start, stop, int(np.abs(np.abs(start-stop) / step)))
