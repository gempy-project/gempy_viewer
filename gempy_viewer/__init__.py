import sys
from .API.plot_api import plot_2d, plot_3d
from .core.plotting_2d_options import Plotting2DOptions

__all__ = ['plot_2d', 'plot_3d']

# Assert at least pyton 3.10
assert sys.version_info[0] >= 3 and sys.version_info[1] >= 10, "GemPy requires Python 3.10 or higher"

if __name__ == '__main__':
    pass
