import matplotlib
import numpy as np

from gempy import GeoModel
from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D


def plot_contacts(plot_2d: Plot2D, gempy_model: GeoModel, ax: matplotlib.axes.Axes, resolution: iter,
                  section_name=None, cell_number=None, direction='y', only_faults: bool = False, **kwargs):
    extent_val = [*ax.get_xlim(), *ax.get_ylim()]
    section_name, cell_number, direction = plot_2d._check_default_section(ax, section_name, cell_number, direction)

    if only_faults:
        raise NotImplementedError('Only faults not implemented yet')
    #     contour_idx = list(self.model._faults.df[self.model._faults.df['isFault'] == True].index)
    # else:
    #     contour_idx = list(self.model._surfaces.df.index)

    zorder = kwargs.get('zorder', 100)

    if section_name is not None:
        _prepare_block_image(ax, extent_val, section_name, zorder)

    elif cell_number is not None:
        _a, _b, _c, _, x, y, _, _ = plot_2d.slice(
            regular_grid=gempy_model.grid.regular_grid,
            direction=direction,
            cell_number=cell_number
        )

        shape = resolution
        c_id = 0  # * color id startpoint
        all_colors = gempy_model.structural_frame.elements_colors_contacts

        for e, block in enumerate(gempy_model.solutions.raw_arrays.scalar_field_matrix):
            _scalar_field_per_surface = np.where(gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e] != 0)
            level = gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e][_scalar_field_per_surface]
            c_id2 = c_id + len(level)

            color_list = all_colors[c_id:c_id2]

            image = block.reshape(shape)[_a, _b, _c].T
            ax.contour(
                image,
                0,
                levels=np.sort(level),
                colors=color_list[::-1],
                linestyles='solid',
                origin='lower',
                extent=extent_val,
                zorder=zorder - (e + len(level))
            )
            
            c_id = c_id2


def _prepare_block_image(ax, extent_val, section_name, zorder):
    if section_name == 'topography':
        shape = self.model._grid.topography.resolution

        scalar_fields = self.model.solutions.geological_map[1:]
        c_id = 0  # color id startpoint

        for e, block in enumerate(scalar_fields):
            level = self.model.solutions.scalar_field_at_surface_points[e][np.where(
                self.model.solutions.scalar_field_at_surface_points[e] != 0)]

            c_id2 = c_id + len(level)  # color id endpoint
            ax.contour(
                block.reshape(shape).T, 0,
                levels=np.sort(level),
                colors=self.cmap.colors[c_id:c_id2][::-1],
                linestyles='solid',
                origin='lower',
                extent=extent_val,
                zorder=zorder - (e + len(level))
            )
            c_id = c_id2

    else:
        l0, l1 = self.model._grid.sections.get_section_args(section_name)
        shape = self.model._grid.sections.df.loc[section_name, 'resolution']
        scalar_fields = self.model.solutions.sections[1:][:, l0:l1]

        c_id = 0  # color id startpoint

        for e, block in enumerate(scalar_fields):
            level = self.model.solutions.scalar_field_at_surface_points[e][np.where(
                self.model.solutions.scalar_field_at_surface_points[e] != 0)]

            # Ignore warning about some scalars not being on the plot since it is very common
            # that an interface does not exit for a given section
            c_id2 = c_id + len(level)  # color id endpoint
            color_list = self.model._surfaces.df.groupby('isActive').get_group(True)['color'][c_id:c_id2][::-1]

            ax.contour(block.reshape(shape).T, 0, levels=np.sort(level),
                       # colors=self.cmap.colors[self.model.surfaces.df['isActive']][c_id:c_id2],
                       colors=color_list,
                       linestyles='solid', origin='lower',
                       extent=extent_val, zorder=zorder - (e + len(level))
                       )
            c_id = c_id2
