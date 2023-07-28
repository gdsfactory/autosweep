import matplotlib.pyplot as plt
import numpy as np

from ta.utils.typing_ext import PathLike


class FigHandler:

    def __init__(self, subplts: tuple = (1, 1)):

        self.fig = plt.figure()
        self.axes = self.fig.subplots(*subplts)

    @property
    def ax(self):
        if isinstance(self.axes, np.ndarray):
            if self.axes.ndim == 1:
                return self.axes[0]
            else:
                return self.axes[0, 0]
        else:
            return self.axes

    def save_fig(self, path: PathLike):
        self.fig.savefig(fname=path)