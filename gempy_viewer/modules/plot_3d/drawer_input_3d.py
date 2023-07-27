import numpy as np
import pyvista as pv

from gempy.core.data.orientations import OrientationsTable
from gempy.core.data.surface_points import SurfacePointsTable
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from matplotlib import colors as mcolors

from gempy_viewer.modules.plot_2d.plot_2d_utils import get_geo_model_cmap


def plot_data(gempy_vista: GemPyToVista, surface_points: SurfacePointsTable, orientations: OrientationsTable, arrows_factor: float,
              elements_colors: list[str], **kwargs):

    plot_surface_points(
        gempy_vista=gempy_vista,
        surface_points=surface_points,
        elements_colors=elements_colors,
        **kwargs
    )
    
    plot_orientations(
        gempy_vista=gempy_vista,
        orientations=orientations,
        elements_colors=elements_colors,
        arrows_factor=arrows_factor,
        **kwargs
    )


def plot_surface_points(
        gempy_vista: GemPyToVista,
        surface_points: SurfacePointsTable,
        elements_colors: list[str],
        render_points_as_spheres=True,
        point_size=10, **kwargs
):
    # Selecting the surfaces to plo
    poly = pv.PolyData(surface_points.xyz)

    # TODO: Check if this is the final solution
    ids = surface_points.ids
    poly['id'] = ids

    _, unique_indices = np.unique(ids, return_index=True)
    unique_ids_in_order = ids[np.sort(unique_indices)]
    cmap = get_geo_model_cmap(np.array(elements_colors)[unique_ids_in_order], reverse=False)

    gempy_vista.surface_points_mesh = poly
    gempy_vista.surface_points_actor = gempy_vista.p.add_mesh(
        mesh=poly,
        cmap=cmap,  # TODO: Add colors
        scalars='id',
        render_points_as_spheres=render_points_as_spheres,
        point_size=point_size,
        show_scalar_bar=False
    )


def plot_orientations(
        gempy_vista: GemPyToVista,
        orientations: OrientationsTable,
        elements_colors: list[str],
        arrows_factor: float,
        clear=True,
        **kwargs
):

    poly = pv.PolyData(orientations.xyz)
    ids = orientations.ids
    poly['id'] = ids
    poly['vectors'] = orientations.grads

    _, unique_indices = np.unique(ids, return_index=True)
    unique_ids_in_order = ids[np.sort(unique_indices)]
    cmap = get_geo_model_cmap(np.array(elements_colors)[unique_ids_in_order], reverse=False)
    
    arrows = poly.glyph(
        orient='vectors',
        scale=False,
        factor=arrows_factor,
    )

    gempy_vista.orientations_actor = gempy_vista.p.add_mesh(
        mesh=arrows,
        cmap=cmap,
        show_scalar_bar=False
    )
    gempy_vista.orientations_mesh = arrows
