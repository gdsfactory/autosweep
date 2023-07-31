import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
import io

from autosweep.utils.typing_ext import PathLike


class FigHandler:
    """
    A class which wraps some matplotlib functionality in order to speed-up plotting within tests. This can also be used
    more generally within jypter notebooks or other scripts as well.
    """

    def __init__(self, subplts: tuple = (1, 1)):
        """

        :param subplts: The shape of supblots to add to this figure:
        :type subplts: tuple, default (1, 1)
        """

        self.fig = plt.figure()
        self.axes = self.fig.subplots(*subplts)

    @property
    def ax(self) -> matplotlib.axes.Axes:
        """
        :return: The axis of there is one plot, or the first axis if there are multiple.
        :rtype: matplotlib.axes.Axes
        """
        if isinstance(self.axes, np.ndarray):
            return self.axes[0] if self.axes.ndim == 1 else self.axes[0, 0]
        else:
            return self.axes

    def save_fig(self, path: PathLike) -> None:
        """
        Saves a figure as a png to a file.

        :param path: The path to the file
        :type path: str or pathlib.Path
        :return: None
        """
        self.fig.savefig(fname=path)

    def to_base64(self) -> str:
        """
        Used to save a png figure in base64 representation for embedding into HTML files.
        :return: The base64 representation of the png
        :rtype: str
        """
        fig_str = io.BytesIO()

        self.fig.savefig(fig_str, format='png')
        fig_str.seek(0)
        return base64.b64encode(fig_str.read()).decode()
