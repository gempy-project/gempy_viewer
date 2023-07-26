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

    Module with classes and methods to perform implicit regional modelling based on
    the potential field method.
    Tested on Ubuntu 16

    Created on 10/11/2019

    @author: Alex Schaaf, Elisa Heim, Miguel de la Varga
"""
# This is for sphenix to find the packages
# sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from typing import Union, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pn

from gempy import GeoModel
from gempy_viewer.API._plot_2d_sections_api import plot_sections
from gempy_viewer.core.data_to_show import DataToShow
from gempy_viewer.core.section_data_2d import SectionData2D
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from gempy_viewer.modules.plot_2d.multi_axis_manager import sections_iterator, orthogonal_sections_iterator
from gempy_viewer.modules.plot_3d.drawer_input_3d import plot_data
from gempy_viewer.modules.plot_2d.plot_2d_utils import get_geo_model_cmap, get_geo_model_norm
from gempy_viewer.modules.plot_3d.plot_3d_utils import set_scalar_bar

try:
    import pyvista as pv
    from gempy_viewer.modules.plot_3d._vista import Vista as Vista

    PYVISTA_IMPORT = True
except ImportError:
    PYVISTA_IMPORT = False

from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D

try:
    import mplstereonet

    mplstereonet_import = True
except ImportError:
    mplstereonet_import = False


def plot_2d(model: GeoModel,
            n_axis=None,
            section_names: list = None,
            cell_number: Union[int | list[int] | str | list[str]] = None,
            direction: Union[str | list[str]] = 'y',
            series_n: Union[int, List[int]] = 0,
            legend: bool = True,
            ve=1,
            block=None,
            regular_grid=None,
            kwargs_topography=None,
            kwargs_regular_grid=None,
            **kwargs):
    """Plot 2-D sections of geomodel.

    Plot cross sections either based on custom section traces or cell number in xyz direction.
    Options to plot lithology block, scalar field or rendered surface lines.
    Input data and topography can be included.

    Args:
        show_block (bool): If True and model has been computed, plot cross section
         of the final model.
        show_values (bool): If True and model has been computed, plot cross section
         of the value... TODO need to add attribute to choose which value to be plot
        model: Geomodel object with solutions.
        n_axis (int): Subplot axis for multiple sections
        section_names (list): Names of predefined custom section traces
        cell_number (list): Position of the array to plot
        direction (str): Cartesian direction to be plotted (xyz)
        series_n (int): number of the scalar field.
        ve (float): vertical exageration
        regular_grid (numpy.ndarray): Numpy array of the size of model.grid.regular_grid
        kwargs_topography (dict):
            * fill_contour
            * hillshade (bool): Calculate and add hillshading using elevation data
            * azdeg (float): azimuth of sun for hillshade
            * altdeg (float): altitude in degrees of sun for hillshade

    Keyword Args:
        legend (bool): If True plot legend. Default True
        show (bool): Call matplotlib show
        show_data (bool): Show original input data. Defaults to True.
        show_results (bool): If False, override show lith, show_calar, show_values
        show_lith (bool): Show lithological block volumes. Defaults to True.
        show_scalar (bool): Show scalar field isolines. Defaults to False.
        show_boundaries (bool): Show surface boundaries as lines. Defaults to True.
        show_topography (bool): Show topography on plot. Defaults to False.

    Returns:
        :class:`gempy.plot.visualization_2d.Plot2D`: Plot2D object

    """

    if kwargs_regular_grid is None:
        kwargs_regular_grid = dict()
    if kwargs_topography is None:
        kwargs_topography = dict()
    if section_names is None and cell_number is None and direction is not None:
        cell_number = ['mid']

    show = kwargs.get('show', True)

    if block is not None:
        import warnings
        regular_grid = block
        warnings.warn('block is going to be deprecated. Use regular grid instead',
                      DeprecationWarning)

    section_names = [] if section_names is None else section_names
    section_names = np.atleast_1d(section_names)
    if cell_number is None:
        cell_number = []
    elif cell_number == 'mid':
        cell_number = ['mid']
    direction = [] if direction is None else direction

    if type(cell_number) != list:
        cell_number = [cell_number]

    if type(direction) != list:
        direction = [direction]

    if n_axis is None:
        n_axis = len(section_names) + len(cell_number)

    if type(series_n) is int:
        series_n = [series_n] * n_axis

    # * Grab from kwargs all the show arguments and create the proper class. This is for backwards compatibility
    can_show_results = model.solutions is not None  # and model.solutions.lith_block.shape[0] != 0
    data_to_show = DataToShow(
        n_axis=n_axis,
        show_data=kwargs.get('show_data', True),
        show_results=kwargs.get('show_results', can_show_results),
        show_surfaces=kwargs.get('show_surfaces', True),
        show_lith=kwargs.get('show_lith', True),
        show_scalar=kwargs.get('show_scalar', False),
        show_boundaries=kwargs.get('show_boundaries', True),
        show_topography=kwargs.get('show_topography', False),
        show_section_traces=kwargs.get('show_section_traces', True),
        show_values=kwargs.get('show_values', False),
        show_block=kwargs.get('show_block', False)
    )

    # init e
    e = 0
    # is 10 and 10 because in the ax pos is the second digit
    n_columns_ = 1 if len(section_names) + len(cell_number) < 2 else 2
    n_columns = n_columns_ * 10  # This is for the axis location syntax
    n_rows = (len(section_names) + len(cell_number)) / n_columns_

    n_columns_ = np.max([n_columns_, 1])
    n_rows = np.max([n_rows, 1])

    p = Plot2D()
    p.create_figure(cols=n_columns_, rows=n_rows, **kwargs)  # * This creates fig and axes
    section_data_list: list[SectionData2D] = sections_iterator(
        plot_2d=p,
        gempy_model=model,
        sections_names=section_names,
        n_axis=n_axis,
        n_columns=n_columns,
        ve=ve,
        projection_distance=kwargs.get('projection_distance', 0.2 * model.transform.isometric_scale)
    )

    orthogonal_section_data_list: list[SectionData2D] = orthogonal_sections_iterator(
        initial_axis=len(section_data_list),
        plot_2d=p,
        gempy_model=model,
        direction=direction,
        cell_number=cell_number,
        n_axis=n_axis,
        n_columns=n_columns,
        ve=ve,
        projection_distance=kwargs.get('projection_distance', 0.2 * model.transform.isometric_scale)
    )

    section_data_list.extend(orthogonal_section_data_list)

    plot_sections(
        gempy_model=model,
        sections_data=section_data_list,
        data_to_show=data_to_show,
        series_n=series_n,
        legend=legend,
        kwargs_topography=kwargs_topography,
    )
    if show is True:
        p.fig.show()

    return p


def plot_3d(
        model: GeoModel,
        plotter_type='basic',
        scalar_field: str = None,
        ve=None,
        kwargs_plot_structured_grid=None,
        kwargs_plot_topography=None,
        kwargs_plot_data=None,
        image=False,
        off_screen=False,
        **kwargs
) -> GemPyToVista:
    """Plot 3-D geomodel."""
    # * Grab from kwargs all the show arguments and create the proper class. This is for backwards compatibility
    can_show_results = model.solutions is not None  # and model.solutions.lith_block.shape[0] != 0

    data_to_show = DataToShow(
        n_axis=1,
        show_data=kwargs.get('show_data', True),
        show_results=kwargs.get('show_results', can_show_results),
        show_surfaces=kwargs.get('show_surfaces', True),
        show_lith=kwargs.get('show_lith', True),
        show_scalar=kwargs.get('show_scalar', False),
        show_boundaries=kwargs.get('show_boundaries', True),
        show_topography=kwargs.get('show_topography', False),
        show_section_traces=kwargs.get('show_section_traces', True),
        show_values=kwargs.get('show_values', False),
        show_block=kwargs.get('show_block', False)
    )

    if image is True:
        off_screen = True
        kwargs['off_screen'] = True
        plotter_type = 'basic'
    if kwargs_plot_topography is None:
        kwargs_plot_topography = dict()
    if kwargs_plot_structured_grid is None:
        kwargs_plot_structured_grid = dict()
    if kwargs_plot_data is None:
        kwargs_plot_data = dict()

    fig_path: str = kwargs.get('fig_path', None)

    extent: np.ndarray = model.grid.regular_grid.extent
    
    gempy_vista = GemPyToVista(
        extent=extent,
        plotter_type=plotter_type,
        **kwargs
    )

    # if show_surfaces and len(model.solutions.vertices) != 0:
    #     gpv.plot_surfaces()
    if data_to_show.show_lith is True:
        gpv.plot_structured_grid('lith', **kwargs_plot_structured_grid)
    # if show_scalar is True and model.solutions.scalar_field_matrix.shape[0] != 0:
    #     gpv.plot_structured_grid("scalar", series=scalar_field)
    # 
    if data_to_show.show_data:
        arrow_size = kwargs.get('arrow_size', 10)
        min_axes = np.min(np.diff(extent)[[0, 2, 4]])
        
        foo = get_geo_model_norm(model.structural_frame.number_of_elements)
        plot_data(
            gempy_vista=gempy_vista,
            surface_points=model.structural_frame.surface_points,
            orientations=model.structural_frame.orientations,
            arrows_factor = arrow_size / ( 100/min_axes ),
            cmap=get_geo_model_cmap(model.structural_frame.elements_colors_volumes),
            **kwargs_plot_data
        )

    # if show_topography and model._grid.topography is not None:
    #     gpv.plot_topography(**kwargs_plot_topography)
    
    set_scalar_bar(
        gempy_vista=gempy_vista,
        n_labels=model.structural_frame.number_of_elements,
        surfaces_ids=model.structural_frame.elements_ids -1
    )
    
    if ve is not None:
        gempy_vista.p.set_scale(zscale=ve)

    if fig_path is not None:
        gempy_vista.p.show(screenshot=fig_path)

    if image is True:
        img = gempy_vista.p.show(screenshot=True)
        img = gempy_vista.p.last_image
        plt.imshow(img[1])
        plt.axis('off')
        plt.show(block=False)
        gempy_vista.p.close()

    if off_screen is False:
        gempy_vista.p.show()

    return gempy_vista


def plot_interactive_3d(
        geo_model,
        scalar_field: str = 'all',
        series=None,
        show_topography: bool = False,
        **kwargs,
):
    """Plot interactive 3-D geomodel with three cross sections in subplots.
    Args:
        geo_model: Geomodel object with solutions.
        name (str): Can be either one of the following
                'lith' - Lithology id block.
                'scalar' - Scalar field block.
                'values' - Values matrix block.
        render_topography: Render topography. Defaults to False.
        **kwargs:
    Returns:
        :class:`gempy.plot.vista.GemPyToVista`

    """
    gpv = GemPyToVista(plotter_type='background', shape="1|3")
    gpv.plot_data()
    gpv.plot_structured_grid_interactive(scalar_field=scalar_field, series=series,
                                         render_topography=show_topography, **kwargs)

    return gpv


def plot_section_traces(model):
    """Plot section traces of section grid in 2-D topview (xy).

    Args:
        model: Geomodel object with solutions.

    Returns:
        (Plot2D) Plot2D object
    """
    pst = plot_2d(model, n_axis=1, direction=['z'], cell_number=[-1],
                  show_data=False, show_boundaries=False, show_lith=False, show=False)
    pst.plot_section_traces(pst.axes[0], show_data=False)
    return pst


def plot_stereonet(self, litho=None, planes=True, poles=True,
                   single_plots=False,
                   show_density=False):
    if mplstereonet_import is False:
        raise ImportError(
            'mplstereonet package is not installed. No stereographic projection available.')

    from collections import OrderedDict

    if litho is None:
        litho = self.model._orientations.df['surface'].unique()

    if single_plots is False:
        fig, ax = mplstereonet.subplots(figsize=(5, 5))
        df_sub2 = pn.DataFrame()
        for i in litho:
            df_sub2 = df_sub2.append(self.model._orientations.df[
                                         self.model._orientations.df[
                                             'surface'] == i])

    for formation in litho:
        if single_plots:
            fig = plt.figure(figsize=(5, 5))
            ax = fig.add_subplot(111, projection='stereonet')
            ax.set_title(formation, y=1.1)

        # if series_only:
        # df_sub = self.model.orientations.df[self.model.orientations.df['series'] == formation]
        # else:
        df_sub = self.model._orientations.df[
            self.model._orientations.df['surface'] == formation]

        if poles:
            ax.pole(df_sub['azimuth'] - 90, df_sub['dip'], marker='o',
                    markersize=7,
                    markerfacecolor=self._color_lot[formation],
                    markeredgewidth=1.1, markeredgecolor='gray',
                    label=formation + ': ' + 'pole point')
        if planes:
            ax.plane(df_sub['azimuth'] - 90, df_sub['dip'],
                     color=self._color_lot[formation],
                     linewidth=1.5, label=formation + ': ' + 'azimuth/dip')
        if show_density:
            if single_plots:
                ax.density_contourf(df_sub['azimuth'] - 90, df_sub['dip'],
                                    measurement='poles', cmap='viridis',
                                    alpha=.5)
            else:
                ax.density_contourf(df_sub2['azimuth'] - 90, df_sub2['dip'],
                                    measurement='poles', cmap='viridis',
                                    alpha=.5)

        fig.subplots_adjust(top=0.8)
        handles, labels = ax.get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.9, 1.1))
        ax._grid(True, color='black', alpha=0.25)


def plot_topology(geo_model, edges, centroids, direction="y", scale=True,
                  label_kwargs=None, edge_kwargs=None):
    """Plot the topology adjacency graph in 2-D.

        Args:
            geo_model ([type]): GemPy geomodel instance.
            edges (Set[Tuple[int, int]]): Set of topology edges.
            centroids (Dict[int, Array[int, 3]]): Dictionary of topology id's and
                their centroids.
            direction (Union["x", "y", "z", optional): Section direction.
                Defaults to "y".
            label_kwargs (dict, optional): Keyword arguments for topology labels.
                Defaults to None.
            edge_kwargs (dict, optional): Keyword arguments for topology edges.
                Defaults to None.

        """
    res = geo_model._grid.regular_grid.resolution
    if direction == "y":
        c1, c2 = (0, 2)
        e1 = geo_model._grid.regular_grid.extent[1] - geo_model._grid.regular_grid.extent[0]
        e2 = geo_model._grid.regular_grid.extent[5] - geo_model._grid.regular_grid.extent[4]
        d1 = geo_model._grid.regular_grid.extent[0]
        d2 = geo_model._grid.regular_grid.extent[4]
        # if len(list(centroids.items())[0][1]) == 2:
        #     c1, c2 = (0, 1)
        r1 = res[0]
        r2 = res[2]
    elif direction == "x":
        c1, c2 = (1, 2)
        e1 = geo_model._grid.regular_grid.extent[3] - geo_model._grid.regular_grid.extent[2]
        e2 = geo_model._grid.regular_grid.extent[5] - geo_model._grid.regular_grid.extent[4]
        d1 = geo_model._grid.regular_grid.extent[2]
        d2 = geo_model._grid.regular_grid.extent[4]
        # if len(list(centroids.items())[0][1]) == 2:
        #     c1, c2 = (0, 1)
        r1 = res[1]
        r2 = res[2]
    elif direction == "z":
        c1, c2 = (0, 1)
        e1 = geo_model._grid.regular_grid.extent[1] - geo_model._grid.regular_grid.extent[0]
        e2 = geo_model._grid.regular_grid.extent[3] - geo_model._grid.regular_grid.extent[2]
        d1 = geo_model._grid.regular_grid.extent[0]
        d2 = geo_model._grid.regular_grid.extent[2]
        # if len(list(centroids.items())[0][1]) == 2:
        #     c1, c2 = (0, 1)
        r1 = res[0]
        r2 = res[1]

    tkw = {
        "color"              : "white",
        "fontsize"           : 13,
        "ha"                 : "center",
        "va"                 : "center",
        "weight"             : "ultralight",
        "family"             : "monospace",
        "verticalalignment"  : "center",
        "horizontalalignment": "center",
        "bbox"               : dict(boxstyle='round', facecolor='black', alpha=1),
    }
    if label_kwargs is not None:
        tkw.update(label_kwargs)

    lkw = {
        "linewidth": 1,
        "color"    : "black"
    }
    if edge_kwargs is not None:
        lkw.update(edge_kwargs)

    for a, b in edges:
        # plot edges
        x = np.array([centroids[a][c1], centroids[b][c1]])
        y = np.array([centroids[a][c2], centroids[b][c2]])
        if scale:
            x = x * e1 / r1 + d1
            y = y * e2 / r2 + d2
        plt.plot(x, y, **lkw)

    for node in np.unique(list(edges)):
        x = centroids[node][c1]
        y = centroids[node][c2]
        if scale:
            x = x * e1 / r1 + d1
            y = y * e2 / r2 + d2
        plt.text(x, y, str(node), **tkw)
