import numpy as np

from gempy import GeoModel, Grid
from gempy_engine.core.data.legacy_solutions import LegacySolution
from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D


def plot_scalar_field(plot_2d: Plot2D, gempy_model: GeoModel, ax, block: np.ndarray, resolution: iter,
                      section_name=None, cell_number=None, direction='y', series_n: int = 0, **kwargs):
    extent_val = [*ax.get_xlim(), *ax.get_ylim()]
    section_name, cell_number, direction = plot_2d._check_default_section(ax, section_name, cell_number, direction)

    if section_name is not None:
        image = _prepare_section_image(gempy_model, section_name, series_n=series_n)
    elif cell_number is not None or block is not None:
        _a, _b, _c, _, x, y, _, _ = plot_2d.slice(
            regular_grid=gempy_model.grid.regular_grid,
            direction=direction,
            cell_number=cell_number
        )

        plot_block = block.reshape(resolution)
        image = plot_block[_a, _b, _c].T
    else:
        raise AttributeError

    ax.contour(
        image,
        cmap='autumn',
        extent=extent_val,
        zorder=8,
        **kwargs
    )
    if 'N' in kwargs:
        kwargs.pop('N')
    ax.contourf(
        image,
        cmap='autumn',
        extent=extent_val,
        zorder=7,
        alpha=.8,
        **kwargs
    )

    return ax


def _prepare_section_image(gempy_model: GeoModel, section_name: str, series_n: int = 0):
    legacy_solutions: LegacySolution = gempy_model.solutions.raw_arrays
    grid: Grid = gempy_model.grid

    if section_name == 'topography':
        try:
            image = legacy_solutions.geological_map[1][series_n].reshape(grid.topography.values_2d[:, :, 2].shape).T
        except AttributeError:
            raise AttributeError('Geological map not computed. Activate the topography grid.')
    else:
        assert type(section_name) == str or type(
            section_name) == np.str_, 'section name must be a string of the name of the section'
        assert legacy_solutions.sections is not None, 'no sections for plotting defined'

        l0, l1 = grid.sections.get_section_args(section_name)
        shape = grid.sections.df.loc[section_name, 'resolution']
        image = legacy_solutions.sections[1][l0:l1].reshape(shape[0], shape[1]).T
    return image
