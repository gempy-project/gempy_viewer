import numpy as np
import pyvista as pv
from vtkmodules.util.numpy_support import numpy_to_vtk
import matplotlib.colors as mcolors

from gempy_viewer.core.scalar_data_type import TopographyDataType
from gempy_engine.core.data.legacy_solutions import LegacySolution
from gempy_viewer.modules.plot_3d.vista import GemPyToVista


def plot_topography(
        gempy_vista: GemPyToVista,
        topography: np.ndarray,
        solution: LegacySolution,
        topography_scalar_type: TopographyDataType,
        elements_colors: list[str],
        contours=True,
        **kwargs
):
    """
    Args:
        topography:
        scalars:
        clear:
        **kwargs:
    """
    rgb = False
    polydata = pv.PolyData(topography)

    match topography_scalar_type:
        case TopographyDataType.GEOMAP:
            colors_hex = elements_colors,
            if False: # ! This is the old implementation
                colors_rgb_ = colors_hex.apply(lambda val: list(mcolors.hex2color(val)))
                colors_rgb = pd.DataFrame(colors_rgb_.to_list(), index=colors_hex.index) * 255

                sel = np.round(solution.geological_map[0]).astype(int)

                scalars_val = numpy_to_vtk(colors_rgb.loc[sel], array_type=3)
            else:
                # Convert hex to RGB using list comprehension
                colors_rgb_ = [list(mcolors.hex2color(val)) for val in colors_hex]

                # Multiply by 255 to get RGB values in [0, 255]
                colors_rgb = np.array(colors_rgb_) * 255

                sel = np.round(solution.geological_map[0]).astype(int)

                # Use numpy advanced indexing to get the corresponding RGB values
                selected_colors = colors_rgb[sel]

                # Convert to vtk array
                scalars_val = numpy_to_vtk(selected_colors, array_type=3)
                
            cm = mcolors.ListedColormap(elements_colors)
            rgb = True

            show_scalar_bar = False
            scalars = 'id'

        case TopographyDataType.TOPOGRAPHY:
            scalars_val = topography[:, 2]
            cm = 'terrain'

            show_scalar_bar = True
            scalars = 'height'

        case TopographyDataType.SCALARS:
            raise NotImplementedError('Not implemented yet')
        case _:
            raise AttributeError("Parameter scalars needs to be either 'geomap', 'topography' or 'scalars'")

    polydata.delaunay_2d(inplace=True)
    polydata['id'] = scalars_val
    polydata['height'] = topography[:, 2]

    sbo = gempy_vista.scalar_bar_options
    sbo['position_y'] = .35

    topography_actor = gempy_vista.p.add_mesh(
        polydata,
        scalars=scalars,
        cmap=cm,
        rgb=rgb,
        show_scalar_bar=show_scalar_bar,
        scalar_bar_args=sbo,
        **kwargs
    )

    if contours is True:
        contours = polydata.contour(scalars='height')
        contours_actor = gempy_vista.p.add_mesh(contours, color="white", line_width=3)

        gempy_vista.surface_poly['topography'] = polydata
        gempy_vista.surface_poly['topography_cont'] = contours
        gempy_vista.surface_actors["topography"] = topography_actor
        gempy_vista.surface_actors["topography_cont"] = contours_actor
    return topography_actor
