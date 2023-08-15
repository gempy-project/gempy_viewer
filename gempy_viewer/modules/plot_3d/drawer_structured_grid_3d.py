from typing import Union, Optional

import pyvista as pv
from matplotlib import colors as mcolors
from pyvista import PolyData

from gempy_engine.core.data.raw_arrays_solution import RawArraysSolution
from gempy_viewer.core.scalar_data_type import ScalarDataType
from gempy.core.data.grid_modules import RegularGrid, Topography
from gempy_viewer.modules.plot_3d.vista import GemPyToVista


def plot_structured_grid(
        gempy_vista: GemPyToVista,
        regular_grid: RegularGrid,
        scalar_data_type: ScalarDataType,
        solution: RawArraysSolution,
        cmap: Union[mcolors.Colormap or str],
        active_scalar_field: Optional[str] = None,
        opacity=.5,
        **kwargs
):
    structured_grid: pv.StructuredGrid | pv.PolyData = create_regular_mesh(gempy_vista, regular_grid)

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
    topography_polydata: PolyData = gempy_vista.surface_poly.get('topography', None)
    if topography_polydata is not None:
        structured_grid = structured_grid.clip_surface(
            surface=topography_polydata,
            value=-10,
            crinkle=False,
            invert=False
        )
        
    add_regular_grid_mesh(
        gempy_vista=gempy_vista,
        structured_grid=structured_grid,
        cmap=cmap,
        opacity=opacity,  # BUG pass this as an argument
        **kwargs
    )


def add_regular_grid_mesh(
        gempy_vista: GemPyToVista,
        structured_grid: pv.StructuredGrid,
        cmap: Union[mcolors.Colormap or str],
        opacity: float,
        **kwargs
):

    gempy_vista.regular_grid_actor = gempy_vista.p.add_mesh(
        mesh=structured_grid,
        cmap=cmap,
        # ? scalars=main_scalar, if we prepare the structured grid do we need this arg?
        show_scalar_bar=True,
        scalar_bar_args=gempy_vista.scalar_bar_arguments,
        opacity=opacity,
        **kwargs
    )


def create_regular_mesh(gempy_vista: GemPyToVista, regular_grid: RegularGrid) -> pv.StructuredGrid:
    gempy_vista._grid_values = regular_grid.values

    grid_3d = regular_grid.values.reshape(*regular_grid.resolution, 3).T
    regular_grid_mesh = pv.StructuredGrid(*grid_3d)

    return regular_grid_mesh


def _mask_topography(structured_grid: pv.StructuredGrid, topography: Topography) -> pv.StructuredGrid:
    # ? Obsolete? I am using pyvista clipping and seems to do the job very good.
    threshold = -100
    structured_grid.active_scalars[topography.topography_mask.ravel(order='C')] = threshold - 1

    # ? Is this messing up the data type?
    structured_grid: pv.StructuredGrid = structured_grid.threshold(
        value=threshold,
        method="upper"
    )
    
    return structured_grid


def set_scalar_data(
        data: RawArraysSolution,
        structured_grid: pv.StructuredGrid,
        scalar_data_type: ScalarDataType,
) -> pv.StructuredGrid:
    # Substitute the madness of the previous if with match
    match scalar_data_type:
        case ScalarDataType.LITHOLOGY | ScalarDataType.ALL:
            structured_grid['id'] = data.lith_block - 1  # TODO: check out if the -1 is the actual fix
            # hex_colors = list(self._get_color_lot(is_faults=True, is_basement=True))
            # cmap = mcolors.ListedColormap(hex_colors)
        case ScalarDataType.SCALAR_FIELD | ScalarDataType.ALL:
            scalar_field_ = 'sf_'
            for e in range(data.scalar_field_matrix.shape[0]):
                # TODO: Ideally we will have the group name instead the enumeration
                structured_grid[scalar_field_ + str(e)] = data.scalar_field_matrix[e]

        case ScalarDataType.VALUES | ScalarDataType.ALL:
            scalar_field_ = 'values_'
            for e in range(data.values_matrix.shape[0]):
                structured_grid[scalar_field_ + str(e)] = data.values_matrix[e]

        case _:
            raise ValueError(f'Unknown scalar data type: {scalar_data_type}')

    return structured_grid  # , cmap


def set_active_scalar_fields(structured_grid: pv.StructuredGrid, active_scalar_field: Optional[str]) -> pv.StructuredGrid:
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
    # if update_cmap is True and self.regular_grid_actor is not None:
    #     cmap = 'lith' if scalar_field == 'lith' else 'viridis'
    #     self.set_scalar_field_cmap(cmap=cmap)
    #     arr_ = structured_grid.get_array(scalar_field)
    #     if scalar_field != 'lith':
    #         self.p.add_scalar_bar(title='values')
    #     self.p.update_scalar_bar_range((arr_.min(), arr_.max()))
