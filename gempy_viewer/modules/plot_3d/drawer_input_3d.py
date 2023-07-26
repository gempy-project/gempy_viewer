import numpy as np
import pyvista as pv

from gempy.core.data.orientations import OrientationsTable
from gempy.core.data.surface_points import SurfacePointsTable
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from matplotlib import colors as mcolors


def plot_data(gempy_vista: GemPyToVista, surface_points: SurfacePointsTable, orientations: OrientationsTable, arrows_factor: float,
              cmap: mcolors.Colormap, **kwargs):
    plot_surface_points(
        gempy_vista=gempy_vista,
        surface_points=surface_points,
        cmap=cmap,
        **kwargs
    )
    
    plot_orientations(
        gempy_vista=gempy_vista,
        orientations=orientations,
        cmap=cmap,
        arrows_factor=arrows_factor,
        **kwargs
    )


def plot_surface_points(
        gempy_vista: GemPyToVista,
        surface_points: SurfacePointsTable,
        cmap: mcolors.Colormap,
        render_points_as_spheres=True,
        point_size=10, **kwargs
):
    # Selecting the surfaces to plo
    poly = pv.PolyData(surface_points.xyz)

    # TODO: Check if this is the final solution
    poly['id'] = surface_points.ids

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
        cmap: mcolors.Colormap,
        arrows_factor: float,
        clear=True,
        **kwargs
):

    poly = pv.PolyData(orientations.xyz)
    poly['id'] = orientations.ids
    poly['vectors'] = orientations.grads

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
