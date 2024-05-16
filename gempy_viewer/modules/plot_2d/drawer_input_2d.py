import copy
import warnings

import numpy as np
from matplotlib import pyplot as plt

from gempy_viewer.core.slicer_data import SlicerData
from gempy.core.data.grid_modules import RegularGrid, Sections
from gempy.core.data.grid_modules import Topography
from .plot_2d_utils import slice_cross_section
from .visualization_2d import Plot2D
from gempy.core.data import GeoModel
from gempy.core.data.grid import Grid


def _plot_data(plot_2d: Plot2D, gempy_model: GeoModel, ax, section_name=None, cell_number=None, direction='y',
              legend=True, projection_distance=None):
    warnings.warn('This function is deprecated. Use plot_data instead', DeprecationWarning)
    if projection_distance is None:
        # TODO: This has to be updated to the new location
        projection_distance = 0.2 * gempy_model.transform.isometric_scale

    # TODO: This are not here 
    points = gempy_model.surface_points_copy.df.copy()
    orientations = gempy_model.orientations_copy.df.copy()

    # TODO: This is a weird check to do this deep
    section_name, cell_number, direction = plot_2d._check_default_section(ax, section_name, cell_number, direction)

    if section_name is not None:
        slicer_data: SlicerData = _projection_params_section(
            grid=gempy_model.grid,
            orientations=orientations,
            points=points,
            projection_distance=projection_distance,
            section_name=section_name
        )
    else:
        slicer_data: SlicerData = _projection_params_regular_grid(
            regular_grid=gempy_model.grid.regular_grid,
            cell_number=cell_number,
            direction=direction,
            orientations=orientations,
            points=points,
            projection_distance=projection_distance
        )

    # ! Hack to keep the right X label. I think this has to be here before the plot
    temp_label = copy.copy(ax.xaxis.label)
    
    draw_data(
        ax=ax, 
        surface_points_colors=gempy_model.structural_frame.surface_points_colors_per_item,
        orientations_colors=gempy_model.structural_frame.orientations_colors_per_item,
        orientations=orientations,
        points=points,
        slicer_data=slicer_data
    )
    
    # region others
    if plot_2d.fig.is_legend is False and legend is True or legend == 'force':
        ax.legend(
            handles=[plt.Line2D([0, 0], [0, 0], color=color, marker='o', linestyle='') for color in gempy_model.structural_frame.elements_colors][::-1],
            labels=gempy_model.structural_frame.elements_names,
            numpoints=1
        )
        plot_2d.fig.is_legend = True

    ax.xaxis.label = temp_label
    try:
        ax.legend_.set_frame_on(True)
        ax.legend_.set_zorder(10000)
    except AttributeError:
        pass
    # endregion


# TODO: This could be public and the slice just a class yes!
def draw_data(ax, surface_points_colors: list[str], orientations_colors: list[str],
              orientations: 'pd.DataFrame', points: 'pd.DataFrame', slicer_data: SlicerData):
    
    _draw_surface_points(ax, points, slicer_data, surface_points_colors)
    _draw_orientations(ax, orientations, orientations_colors, slicer_data)


def _draw_orientations(ax, orientations, orientations_colors, slicer_data):
    sel_ori = orientations[slicer_data.select_projected_o]
    aspect = np.subtract(*ax.get_ylim()) / np.subtract(*ax.get_xlim())
    min_axis = 'width' if aspect < 1 else 'height'
    ax.quiver(
        sel_ori[slicer_data.x],
        sel_ori[slicer_data.y],
        sel_ori[slicer_data.Gx],
        sel_ori[slicer_data.Gy],
        pivot="tail",
        scale_units=min_axis,
        scale=30,
        color=np.array(orientations_colors)[slicer_data.select_projected_o],
        edgecolor='k',
        headwidth=8,
        linewidths=1,
        zorder=102
    )


def _draw_surface_points(ax, points, slicer_data, surface_points_colors):
    points_df = points[slicer_data.select_projected_p]
    ax.scatter(
        points_df[slicer_data.x],
        points_df[slicer_data.y],
        c=(np.array(surface_points_colors)[slicer_data.select_projected_p]),
        s=70,
        edgecolors='white',
        zorder=102
    )


def _projection_params_regular_grid(regular_grid: RegularGrid, cell_number, direction, orientations, points,
                                    projection_distance) -> SlicerData:
    if direction == 'x' or direction == 'X':
        arg_ = 0
        dx = regular_grid.dx
        dir = 'X'
    elif direction == 'y' or direction == 'Y':
        arg_ = 2
        dx = regular_grid.dy
        dir = 'Y'
    elif direction == 'z' or direction == 'Z':
        arg_ = 4
        dx = regular_grid.dz
        dir = 'Z'
    else:
        raise AttributeError('Direction must be x, y, z')

    _loc = regular_grid.extent[arg_] + dx * int(regular_grid.resolution[0] / 2)
    cartesian_point_dist = points[dir] - _loc
    cartesian_ori_dist = orientations[dir] - _loc

    _a, _b, _c, _, x, y, Gx, Gy = slice_cross_section(
        regular_grid=regular_grid,
        direction=direction,
        cell_number=cell_number
    )
    select_projected_p = cartesian_point_dist < projection_distance
    select_projected_o = cartesian_ori_dist < projection_distance
    
    slice_data = SlicerData(
        x=x,
        y=y,
        Gx=Gx,
        Gy=Gy,
        select_projected_p=select_projected_p,
        select_projected_o=select_projected_o,
        regular_grid_x_idx=_a,
        regular_grid_y_idx=_b,
        regular_grid_z_idx=_c
    )

    return slice_data


def _projection_params_section(grid: Grid, orientations: 'pd.DataFrame', points: 'pd.DataFrame',
                               projection_distance: float, section_name: str) -> SlicerData:
    if section_name == 'topography':
        Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y = _projection_params_topography(
            topography=grid.topography,
            orientations=orientations,
            points=points,
            projection_distance=projection_distance,
        )
    else:
        # Project points:
        sections: Sections = grid.sections
        shift = np.asarray(sections.df.loc[section_name, 'start'])
        end_point = np.atleast_2d(np.asarray(sections.df.loc[section_name, 'stop']) - shift)
        A_rotate = np.dot(end_point.T, end_point) / sections.df.loc[section_name, 'dist'] ** 2

        points_x_y = points[['X', 'Y']]
        orientations_x_y = orientations[['X', 'Y']]
    
        perpe_sqdist = ((np.dot(A_rotate, (points_x_y).T).T - points_x_y) ** 2).sum(axis=1)
        cartesian_point_dist = np.sqrt(perpe_sqdist)
        perpe_sqdist = ((np.dot(A_rotate, (orientations_x_y).T).T - orientations_x_y) ** 2).sum(axis=1)
        cartesian_ori_dist = np.sqrt(perpe_sqdist)

        # These are the coordinates of the data projected on the section
        cartesian_point = np.dot(A_rotate, (points_x_y - shift).T).T
        cartesian_ori = np.dot(A_rotate, (orientations_x_y - shift).T).T

        # Since we plot only the section we want the norm of those coordinates
        points['X'] = np.linalg.norm(cartesian_point, axis=1)
        orientations['X'] = np.linalg.norm(cartesian_ori, axis=1)
        x, y, Gx, Gy = 'X', 'Z', 'G_x', 'G_z'

    select_projected_p = cartesian_point_dist < projection_distance
    select_projected_o = cartesian_ori_dist < projection_distance

    slicer_data = SlicerData(
        x=x,
        y=y,
        Gx=Gx,
        Gy=Gy,
        select_projected_p=select_projected_p,
        select_projected_o=select_projected_o
    )

    return slicer_data


def _projection_params_topography(topography: Topography, orientations, points, projection_distance, topography_compression: int = 5000):
    from gempy_viewer.optional_dependencies import require_scipy
    scipy = require_scipy()
    dd = scipy.spatial.distance
    decimation_aux = int(topography.values.shape[0] / topography_compression)
    tpp = topography.values[::decimation_aux + 1, :]
    cdist_sp = dd.cdist(
        XA=tpp,
        XB=points[['X', 'Y', 'Z']])
    cartesian_point_dist = (cdist_sp < projection_distance).sum(axis=0).astype(bool)
    cdist_ori = dd.cdist(
        XA=tpp,
        XB=orientations[['X', 'Y', 'Z']]
    )
    cartesian_ori_dist = (cdist_ori < projection_distance).sum(axis=0).astype(bool)
    x, y, Gx, Gy = 'X', 'Y', 'G_x', 'G_y'
    return Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y
