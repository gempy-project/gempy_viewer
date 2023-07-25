﻿import numpy as np

from gempy_viewer.core.slicer_data import SlicerData
from gempy import GeoModel, Grid
from gempy_engine.core.data.legacy_solutions import LegacySolution
from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D


def plot_regular_grid_scalar_field(ax, slicer_data: SlicerData, block: np.ndarray, resolution: iter, **kwargs):
    extent_val = [*ax.get_xlim(), *ax.get_ylim()]

    plot_block = block.reshape(resolution)
    image = plot_block[
        slicer_data.regular_grid_x_idx,
        slicer_data.regular_grid_y_idx,
        slicer_data.regular_grid_z_idx
    ].T


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


def plot_section_scalar_field(gempy_model: GeoModel, ax, section_name=None, series_n: int = 0, **kwargs):
    extent_val = [*ax.get_xlim(), *ax.get_ylim()]

    image = _prepare_section_image(gempy_model, section_name, series_n=series_n)

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
