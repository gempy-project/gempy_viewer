import matplotlib
import numpy as np

from gempy.core.data import GeoModel
from gempy_engine.core.backend_tensor import BackendTensor
from gempy_viewer.core.slicer_data import SlicerData
from gempy_viewer.modules.plot_2d.drawer_scalar_field_2d import _prepare_section_image


def plot_regular_grid_contacts(gempy_model: GeoModel, ax: matplotlib.axes.Axes, slicer_data: SlicerData, resolution: iter,
                               only_faults: bool = False, kwargs=None):
    if only_faults:
        raise NotImplementedError('Only faults not implemented yet')
    #     contour_idx = list(self.model._faults.df[self.model._faults.df['isFault'] == True].index)
    # else:
    #     contour_idx = list(self.model._surfaces.df.index)
    if kwargs is None:
        kwargs = {}

    zorder = kwargs.get('zorder', 100)
    contour_colors = kwargs.get('contour_colors', None)

    shape = resolution
    c_id = 0  # * color id startpoint
    all_colors = contour_colors if contour_colors is not None else gempy_model.structural_frame.elements_colors_contacts

    for e, block in enumerate(gempy_model.solutions.raw_arrays.scalar_field_matrix):
        _scalar_field_per_surface = np.where(gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e] != 0)
        level = gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e][_scalar_field_per_surface]
        c_id2 = c_id + len(level)

        color_list = all_colors[c_id:c_id2]

        image = block.reshape(shape)[
            slicer_data.regular_grid_x_idx,
            slicer_data.regular_grid_y_idx,
            slicer_data.regular_grid_z_idx
        ].T

        contour_set = ax.contour(
            image,
            0,
            levels=np.sort(level),
            colors=color_list[::-1],
            linestyles='solid',
            origin='lower',
            extent=[*ax.get_xlim(), *ax.get_ylim()],
            zorder=zorder - (e + len(level)),
            **kwargs
        )


        c_id = c_id2


def plot_section_contacts(gempy_model: GeoModel, ax: matplotlib.axes.Axes, section_name: str, kwargs=None):
    if kwargs is None:
        kwargs = {}

    zorder = kwargs.get('zorder', 100)
    contour_colors = kwargs.get('contour_colors', None)

    extent_val = [*ax.get_xlim(), *ax.get_ylim()]
    all_colors = contour_colors if contour_colors is not None else gempy_model.structural_frame.elements_colors_contacts

    c_id = 0  # * color id startpoint

    for e, block in enumerate(gempy_model.solutions.raw_arrays.scalar_field_matrix):
        _scalar_field_per_surface = np.where(gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e] != 0)
        level = gempy_model.solutions.raw_arrays.scalar_field_at_surface_points[e][_scalar_field_per_surface]
        c_id2 = c_id + len(level)

        color_list = all_colors[c_id:c_id2]

        if len(level) > 0:
            image = _prepare_section_image(gempy_model, section_name, series_n=e)
            image = BackendTensor.t.to_numpy(image)

            ax.contour(
                image,
                0,
                levels=np.sort(level),
                colors=color_list[::-1],
                linestyles='solid',
                origin='lower',
                extent=extent_val,
                zorder=zorder - (e + len(level)),
                **kwargs
            )

        c_id = c_id2
