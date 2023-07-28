import numpy as np


def find_nearest_idx(array, val) -> int:
    return np.abs(array - val).argmin()


def find_3_idxs(array, val) -> tuple[int, int] | tuple[int, int, int]:
    idx = find_nearest_idx(array=array, val=val)

    if idx == 0:
        return 0, 1
    elif idx == len(array) - 1:
        return idx-1, idx
    else:
        return idx-1, idx, idx+1
