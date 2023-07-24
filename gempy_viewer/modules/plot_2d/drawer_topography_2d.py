import warnings

import numpy as np

from gempy import GeoModel, Grid
from modules.plot_2d.visualization_2d import Plot2D

from gempy.core.grid_modules.grid_types import Sections, RegularGrid
from optional_dependencies import require_skimage


def plot_topography(
        plot_2d: Plot2D,
        gempy_model: GeoModel,
        ax,
        fill_contour=False,
        contour=True,
        section_name=None,
        cell_number=None,
        direction='y',
        block=None,
        **kwargs):
    warnings.warn('This method is deprecated. Use plot_topography_2d instead', DeprecationWarning)

    hillshade = kwargs.get('hillshade', True)
    azdeg = kwargs.get('azdeg', 0)
    altdeg = kwargs.get('altdeg', 0)
    cmap = kwargs.get('cmap', 'terrain')

    section_name, cell_number, direction = plot_2d._check_default_section(ax, section_name, cell_number, direction)

    grid: Grid = gempy_model.grid
    regular_grid: RegularGrid = grid.regular_grid
    
    if section_name is not None and section_name != 'topography':
        sections: Sections = grid.sections
        p1 = sections.df.loc[section_name, 'start']
        p2 = sections.df.loc[section_name, 'stop']
        x, y, z = plot_2d._slice_topo_4_sections(
            grid=grid,
            p1=p1,
            p2=p2,
            resolution=grid.topography.resolution[0])

        pseudo_x = np.linspace(0, sections.df.loc[section_name, 'dist'], z.shape[0])
        a = np.vstack((pseudo_x, z)).T
        xy = np.append(a,
                       ([sections.df.loc[section_name, 'dist'], a[:, 1][-1]],
                        [sections.df.loc[section_name, 'dist'],
                         regular_grid.extent[5]],
                        [0, regular_grid.extent[5]],
                        [0, a[:, 1][0]])).reshape(-1, 2)

        ax.fill(xy[:, 0], xy[:, 1], 'k', zorder=10)

    elif section_name == 'topography':
        skimage = require_skimage()
        from gempy_viewer.modules.plot_2d.helpers import add_colorbar
        topo = grid.topography
        topo_super_res = skimage.transform.resize(
            topo.values_2d,
            (1600, 1600),
            order=3,
            mode='edge',
            anti_aliasing=True, preserve_range=False)

        values = topo_super_res[:, :, 2].T
        if contour is True:
            CS = ax.contour(values, extent=(topo.extent[:4]),
                            colors='k', linestyles='solid', origin='lower')
            ax.clabel(CS, inline=1, fontsize=10, fmt='%d')
        if fill_contour is True:
            CS2 = ax.contourf(values, extent=(topo.extent[:4]), cmap=cmap)
            add_colorbar(axes=ax, label='elevation [m]', cs=CS2)

        if hillshade is True:
            from matplotlib.colors import LightSource

            ls = LightSource(azdeg=azdeg, altdeg=altdeg)
            hillshade_topography = ls.hillshade(values)
            ax.imshow(hillshade_topography, origin='lower', extent=topo.extent[:4], alpha=0.5, zorder=11,
                      cmap='gray')

    elif cell_number is not None or block is not None:
        p1, p2 = plot_2d.calculate_p1p2(
            regular_grid=regular_grid,
            direction=direction,
            cell_number=cell_number
        )
        
        resx = regular_grid.resolution[0]
        resy = regular_grid.resolution[1]

        try:
            x, y, z = plot_2d._slice_topo_4_sections(
                grid=grid,
                p1=p1,
                p2=p2,
                resolution=resx
            )

            if direction == 'x':
                a = np.vstack((y, z)).T
                ext = regular_grid.extent[[2, 3]]
            elif direction == 'y':
                a = np.vstack((x, z)).T
                ext = regular_grid.extent[[0, 1]]
            else:
                raise NotImplementedError
            a = np.append(a,
                          ([ext[1], a[:, 1][-1]],
                           [ext[1], regular_grid.extent[5]],
                           [ext[0], regular_grid.extent[5]],
                           [ext[0], a[:, 1][0]]))
            line = a.reshape(-1, 2)
            ax.fill(line[:, 0], line[:, 1], color='k')
        except IndexError:
            warnings.warn('Topography needs to be a raster to be able to plot it'
                          'in 2D sections')
    return ax
