import copy

import numpy as np
from matplotlib import pyplot as plt
import scipy.spatial.distance as dd

from .visualization_2d import Plot2D
from gempy import GeoModel
from gempy.core.grid import Grid


def plot_data(plot_2d: Plot2D, gempy_model: GeoModel, ax, section_name=None, cell_number=None, direction='y',
              legend=True, projection_distance=None, **kwargs):
    
    if projection_distance is None:
        # TODO: This has to be updated to the new location
        projection_distance = 0.2 * gempy_model.transform.isometric_scale

    # plot_2d.update_colot_lot()

    # TODO: This are not here 
    points = gempy_model.surface_points.df.copy()
    orientations = gempy_model.orientations.df.copy()

    # TODO: This is a weird check to do this deep
    section_name, cell_number, direction = plot_2d._check_default_section(ax, section_name, cell_number, direction)

    if section_name is not None:
        Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y = _plot_section(gempy_model, kwargs, orientations, plot_2d, points, projection_distance, section_name)
    else:
        Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y = _plot_regular_grid(cell_number, direction, orientations, plot_2d, points)

    select_projected_p = cartesian_point_dist < projection_distance
    select_projected_o = cartesian_ori_dist < projection_distance

    # Hack to keep the right X label:
    temp_label = copy.copy(ax.xaxis.label)

    points_df = points[select_projected_p]

    _colors = points_df['surface'].map(plot_2d._color_lot)
    points_df['colors'] = _colors

    points_df.plot.scatter(
        x=x, y=y, ax=ax,
        c=_colors,
        s=70,
        zorder=102,
        edgecolors='white',
        colorbar=False
    )

    if plot_2d.fig.is_legend is False and legend is True or legend == 'force':
        markers = [plt.Line2D([0, 0], [0, 0], color=color, marker='o', linestyle='') for color in plot_2d._color_lot.values()]
        ax.legend(markers, plot_2d._color_lot.keys(), numpoints=1)
        plot_2d.fig.is_legend = True
        
    ax.xaxis.label = temp_label

    sel_ori = orientations[select_projected_o]

    aspect = np.subtract(*ax.get_ylim()) / np.subtract(*ax.get_xlim())
    min_axis = 'width' if aspect < 1 else 'height'

    ax.quiver(
        sel_ori[x], sel_ori[y], sel_ori[Gx], sel_ori[Gy],
        pivot="tail",
        scale_units=min_axis,
        scale=30,
        color=sel_ori['surface'].map(plot_2d._color_lot),
        edgecolor='k',
        headwidth=8,
        linewidths=1,
        zorder=102
    )

    try:
        ax.legend_.set_frame_on(True)
        ax.legend_.set_zorder(10000)
    except AttributeError:
        pass


def _plot_regular_grid(cell_number, direction, orientations, plot_2d, points):
    if cell_number is None:
        cell_number = int(plot_2d.model._grid.regular_grid.resolution[0] / 2)
    elif cell_number == 'mid':
        cell_number = int(plot_2d.model._grid.regular_grid.resolution[0] / 2)
    if direction == 'x' or direction == 'X':
        arg_ = 0
        dx = plot_2d.model._grid.regular_grid.dx
        dir = 'X'
    elif direction == 'y' or direction == 'Y':
        arg_ = 2
        dx = plot_2d.model._grid.regular_grid.dy
        dir = 'Y'
    elif direction == 'z' or direction == 'Z':
        arg_ = 4
        dx = plot_2d.model._grid.regular_grid.dz
        dir = 'Z'
    else:
        raise AttributeError('Direction must be x, y, z')
    _loc = plot_2d.model._grid.regular_grid.extent[arg_] + dx * cell_number
    cartesian_point_dist = points[dir] - _loc
    cartesian_ori_dist = orientations[dir] - _loc
    x, y, Gx, Gy = plot_2d._slice(direction)[4:]
    return Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y


def _plot_section(gempy_model, kwargs, orientations, plot_2d, points, projection_distance, section_name):
    if section_name == 'topography':
        Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y = _plot_topography(gempy_model, kwargs, orientations, points, projection_distance)
    else:
        # Project points:
        shift = np.asarray(plot_2d.model._grid.sections.df.loc[section_name, 'start'])
        end_point = np.atleast_2d(np.asarray(plot_2d.model._grid.sections.df.loc[section_name, 'stop']) - shift)
        A_rotate = np.dot(end_point.T, end_point) / plot_2d.model._grid.sections.df.loc[section_name, 'dist'] ** 2

        perpe_sqdist = ((np.dot(A_rotate, (points[['X', 'Y']]).T).T - points[['X', 'Y']]) ** 2).sum(axis=1)
        cartesian_point_dist = np.sqrt(perpe_sqdist)

        cartesian_ori_dist = np.sqrt(((np.dot(
            A_rotate, (orientations[['X', 'Y']]).T).T - orientations[['X', 'Y']]) ** 2).sum(axis=1))

        # These are the coordinates of the data projected on the section
        cartesian_point = np.dot(A_rotate, (points[['X', 'Y']] - shift).T).T
        cartesian_ori = np.dot(A_rotate, (orientations[['X', 'Y']] - shift).T).T

        # Since we plot only the section we want the norm of those coordinates
        points['X'] = np.linalg.norm(cartesian_point, axis=1)
        orientations['X'] = np.linalg.norm(cartesian_ori, axis=1)
        x, y, Gx, Gy = 'X', 'Z', 'G_x', 'G_z'
    return Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y


def _plot_topography(gempy_model, kwargs, orientations, points, projection_distance):
    topo_comp = kwargs.get('topo_comp', 5000)
    grid: Grid = gempy_model.grid
    decimation_aux = int(grid.topography.values.shape[0] / topo_comp)
    tpp = grid.topography.values[::decimation_aux + 1, :]
    cdist_sp = dd.cdist(
        XA=tpp,
        XB=points.df[['X', 'Y', 'Z']])
    cartesian_point_dist = (cdist_sp < projection_distance).sum(axis=0).astype(bool)
    cdist_ori = dd.cdist(
        XA=tpp,
        XB=orientations.df[['X', 'Y', 'Z']]
    )
    cartesian_ori_dist = (cdist_ori < projection_distance).sum(axis=0).astype(bool)
    x, y, Gx, Gy = 'X', 'Y', 'G_x', 'G_y'
    return Gx, Gy, cartesian_ori_dist, cartesian_point_dist, x, y
