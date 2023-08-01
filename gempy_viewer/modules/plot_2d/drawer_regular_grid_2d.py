import matplotlib.colors as mcolors
import numpy as np

from gempy import GeoModel, Grid
from gempy_engine.core.data.legacy_solutions import LegacySolution
from gempy_viewer.core.slicer_data import SlicerData


# TODO: This name seems bad. This is plotting area basically?
def plot_regular_grid_area(ax, slicer_data: SlicerData, block: np.ndarray, resolution: iter,
                      cmap: mcolors.Colormap, norm: mcolors.Normalize):
    
    plot_block = block.reshape(resolution)
    image = plot_block[
        slicer_data.regular_grid_x_idx,
        slicer_data.regular_grid_y_idx,
        slicer_data.regular_grid_z_idx].T

    ax.imshow(
        image,
        origin='lower',
        zorder=-100,
        cmap=cmap,
        norm=norm,
        extent=[*ax.get_xlim(), *ax.get_ylim()]
    )
    
    return ax


def plot_section_area(gempy_model: GeoModel, ax, section_name: str, cmap: mcolors.Colormap, norm: mcolors.Normalize):
    image = _prepare_section_image(gempy_model, section_name)
    ax.imshow(
        image,
        origin='lower',
        zorder=-100,
        cmap=cmap,
        norm=norm,
        extent=[*ax.get_xlim(), *ax.get_ylim()]
    )

    return ax


def _prepare_section_image(gempy_model: GeoModel, section_name: str):
    legacy_solutions: LegacySolution = gempy_model.solutions.raw_arrays
    grid: Grid = gempy_model.grid
    
    if section_name == 'topography':
        try:
            image = legacy_solutions.geological_map.reshape(grid.topography.values_2d[:, :, 2].shape).T
        except AttributeError:
            raise AttributeError('Geological map not computed. Activate the topography grid.')
    else:
        assert type(section_name) == str or type(
            section_name) == np.str_, 'section name must be a string of the name of the section'
        assert legacy_solutions.sections is not None, 'no sections for plotting defined'

        l0, l1 = grid.sections.get_section_args(section_name)
        shape = grid.sections.df.loc[section_name, 'resolution']
        image = legacy_solutions.sections[l0:l1].reshape(shape[0], shape[1]).T
    return image
