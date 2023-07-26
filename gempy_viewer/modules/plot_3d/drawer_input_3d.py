import pyvista as pv

from gempy.core.data.surface_points import SurfacePointsTable
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from matplotlib import colors as mcolors


def plot_data(gempy_vista: GemPyToVista, surface_points: SurfacePointsTable, cmap: mcolors.Colormap, orientations=None, **kwargs):
    plot_surface_points(
        gempy_vista=gempy_vista,
        surface_points=surface_points,
        cmap=cmap,
        **kwargs
    )

    # self.set_scalar_bar()
    # if self.model.orientations.df.shape[0] != 0:
    #     self.plot_orientations(surfaces=surfaces, orientations=orientations, **kwargs)


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
        cmap=cmap, # TODO: Add colors
        scalars='id',
        render_points_as_spheres=render_points_as_spheres,
        point_size=point_size,
        show_scalar_bar=False
    )
    # self.set_scalar_bar()

    # r = self.surface_points_actor
    # self.set_bounds()
    # return r
