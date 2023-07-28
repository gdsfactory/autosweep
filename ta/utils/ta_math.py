import numpy as np
from ta.utils import typing_ext


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
