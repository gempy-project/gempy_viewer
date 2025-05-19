from typing import Union, Optional

import numpy as np
from matplotlib import colors as mcolors

from gempy_engine.core.data.raw_arrays_solution import RawArraysSolution
from gempy_viewer.core.scalar_data_type import ScalarDataType
from gempy.core.data.grid_modules import Topography
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from gempy_viewer.optional_dependencies import require_pyvista


def plot_structured_grid(
        gempy_vista: GemPyToVista,
        vtk_formated_regular_mesh: np.ndarray,
        resolution: np.ndarray,
        scalar_data_type: ScalarDataType,
        solution: RawArraysSolution,
        cmap: Union[mcolors.Colormap or str],
        active_scalar_field: Optional[str] = None,
        opacity=.5,
        **kwargs
):
    pv = require_pyvista()

    grid_3d = vtk_formated_regular_mesh.reshape(*(resolution + 1), 3).T
    structured_grid = pv.StructuredGrid(*grid_3d)

    # Set the scalar field-Activate it-getting cmap?
    structured_grid = set_scalar_data(
        structured_grid=structured_grid,
        data=solution,
        scalar_data_type=scalar_data_type
    )

    structured_grid = set_active_scalar_fields(
        structured_grid=structured_grid,
        active_scalar_field=active_scalar_field
    )
    topography_polydata: pv.PolyData = gempy_vista.surface_poly.get('topography', None)
    if topography_polydata is not None:
        structured_grid = structured_grid.clip_surface(
            surface=topography_polydata,
            value=-10,
            crinkle=False,
            invert=True
        )
        
    if active_scalar_field == 'lith':
        gempy_vista.regular_grid_actor = gempy_vista.p.add_mesh(
            mesh=structured_grid,
            show_scalar_bar=False,
            interpolate_before_map=True,
            opacity=opacity,
            **kwargs
        )
    else:
        gempy_vista.regular_grid_actor = gempy_vista.p.add_mesh(
            mesh=structured_grid,
            cmap=cmap,
            show_scalar_bar=True,
            interpolate_before_map=True,
            opacity=opacity,
            **kwargs
        )
    


def _mask_topography(structured_grid: "pv.StructuredGrid", topography: Topography) -> "pv.StructuredGrid":
    # ? Obsolete? I am using pyvista clipping and seems to do the job very good.
    threshold = -100
    structured_grid.active_scalars[topography.topography_mask.ravel(order='C')] = threshold - 1

    # ? Is this messing up the data type?
    pv = require_pyvista()
    structured_grid: pv.StructuredGrid = structured_grid.threshold(
        value=threshold,
        method="upper"
    )

    return structured_grid


def set_scalar_data(
        data: RawArraysSolution,
        structured_grid: "pv.StructuredGrid",
        scalar_data_type: ScalarDataType,
) -> "pv.StructuredGrid":
    
    # Substitute the madness of the previous if with match
    match scalar_data_type:
        case ScalarDataType.LITHOLOGY | ScalarDataType.ALL:
            max_lith = data.n_surfaces # (for basement)
            block_ = max_lith - (data.lith_block - 1)
            structured_grid.cell_data['id'] = block_
        case ScalarDataType.SCALAR_FIELD | ScalarDataType.ALL:
            scalar_field_ = 'sf_'
            for e in range(data.scalar_field_matrix.shape[0]):
                # TODO: Ideally we will have the group name instead the enumeration
                array1 = data.scalar_field_matrix[e]
                structured_grid[scalar_field_ + str(e)] = array1
        case ScalarDataType.VALUES | ScalarDataType.ALL:
            scalar_field_ = 'values_'
            for e in range(data.values_matrix.shape[0]):
                array2 = data.values_matrix[e]
                structured_grid[scalar_field_ + str(e)] = array2
        case _:
            raise ValueError(f'Unknown scalar data type: {scalar_data_type}')

    return structured_grid  # , cmap


def set_active_scalar_fields(structured_grid: "pv.StructuredGrid", active_scalar_field: Optional[str]) -> "pv.StructuredGrid":
    if active_scalar_field is None:
        active_scalar_field = structured_grid.array_names[0]

    if active_scalar_field == 'lith':
        active_scalar_field = 'id'

    # Set the scalar field active
    try:
        structured_grid.set_active_scalars(active_scalar_field)
    except ValueError:
        raise AttributeError('The scalar field provided does not exist. Please pass '
                             'a valid field: {}'.format(structured_grid.array_names))
    return structured_grid
