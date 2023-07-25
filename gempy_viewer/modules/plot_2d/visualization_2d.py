"""
    This file is part of gempy.

    gempy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gempy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with gempy.  If not, see <http://www.gnu.org/licenses/>.


Module with classes and methods to visualized structural geology data and potential fields of the regional modelling based on
the potential field method.

@author: Miguel de la Varga
"""

import warnings

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context('talk')
plt.style.use(['seaborn-v0_8-white', 'seaborn-v0_8-talk'])

warnings.filterwarnings("ignore", message="No contour levels were found")


# ! Missing a function? Check gempy_legacy
class Plot2D:
    # _color_lot: dict
    axes: list[plt.Axes]

    def __init__(self):
        # TODO: Moving this to plotting options
        self.axes = list()

    @staticmethod
    def remove(ax):
        while len(ax.collections) != 0:
            list(map(lambda x: x.remove(), ax.collections))

    def create_figure(self, figsize=None, textsize=None, **kwargs):
        """
        Create the figure.

        Args:
            figsize:
            textsize:

        Returns:
            figure, list axes, subgrid values
        """
        cols = kwargs.get('cols', 1)
        rows = kwargs.get('rows', 1)

        figsize, self.ax_labelsize, _, self.xt_labelsize, self.linewidth, _ = _scale_fig_size(
            figsize, textsize, rows, cols)
        self.fig = plt.figure(figsize=figsize, constrained_layout=False)
        self.fig.is_legend = False

        return self.fig, self.axes  # , self.gs_0
