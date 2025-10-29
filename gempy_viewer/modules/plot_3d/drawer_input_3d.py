import numpy as np

from gempy.core.data import GeoModel
from gempy.core.data.orientations import OrientationsTable
from gempy.core.data.surface_points import SurfacePointsTable
from matplotlib.colors import ListedColormap

from gempy_viewer.modules.plot_2d.plot_2d_utils import get_geo_model_cmap
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from gempy_viewer.optional_dependencies import require_pyvista


def plot_data(gempy_vista: GemPyToVista,
              model: GeoModel,
              arrows_factor: float,
              show_nugget_effect: bool,
              transformed_data: bool = False,
              **kwargs):
    if transformed_data:
        surface_points_copy = model.surface_points_copy_transformed
        orientations_copy = model.orientations_copy_transformed
    else:
        surface_points_copy = model.surface_points_copy
        orientations_copy = model.orientations_copy

    plot_surface_points(
        gempy_vista=gempy_vista,
        surface_points=surface_points_copy,
        element_colors=model.structural_frame.elements_colors,
        show_nugget_effect=show_nugget_effect
    )

    plot_orientations(
        gempy_vista=gempy_vista,
        orientations=orientations_copy,
        surface_points=surface_points_copy,
        arrows_factor=arrows_factor,
        element_colors=model.structural_frame.elements_colors
    )


def plot_surface_points(
        gempy_vista: GemPyToVista,
        surface_points: SurfacePointsTable,
        render_points_as_spheres=True,
        element_colors=None,
        point_size=10,
        show_nugget_effect: bool = False,
):
    # Selecting the surfaces to plot
    xyz = surface_points.xyz
    if transfromed_data := False:  # TODO: Expose this to user
        xyz = surface_points.model_transform.apply(xyz)

    pv = require_pyvista()
    poly = pv.PolyData(xyz)

    ids = surface_points.ids
    if ids.shape[0] == 0:
        return
    vectorize_ids = _vectorize_ids(ids, ids)
    poly['id'] = vectorize_ids

    gempy_vista.surface_points_mesh = poly
    gempy_vista.surface_points_actor = gempy_vista.p.add_mesh(
        mesh=poly,
        scalars='id',
        render_points_as_spheres=render_points_as_spheres,
        point_size=point_size,
        show_scalar_bar=False,
        cmap=(ListedColormap(element_colors)),
        clim=(-0.5, np.unique(vectorize_ids).shape[0] + .5)
    )


    if show_nugget_effect is True:
        nugget_effect = surface_points.nugget
        poly2 = pv.PolyData(xyz)
        poly2['Nugget (smoother)'] = nugget_effect
        # normalize nugget to [0,1]
        mn, mx = nugget_effect.min(), nugget_effect.max()
        gempy_vista.p.add_mesh(
            poly2,
            scalars='Nugget (smoother)',
            cmap='inferno',
            style='points_gaussian',
            log_scale=True, 
            point_size=10,
            opacity=((nugget_effect - mn) / (mx - mn))
        )


def plot_orientations(
        gempy_vista: GemPyToVista,
        orientations: OrientationsTable,
        surface_points: SurfacePointsTable,
        arrows_factor: float,
        element_colors=None,
        arrow_scale_mode='fixed',  # 'fixed' or 'vector'
        arrow_opacity=1.0,
        show_arrow_outline=True,
        outline_color='white',
        outline_width=1,
):
    orientations_xyz = orientations.xyz
    orientations_grads = orientations.grads

    if orientations_xyz.shape[0] == 0:
        return

    pv = require_pyvista()
    poly = pv.PolyData(orientations_xyz)

    vectorize_ids = _vectorize_ids(
        mapping_ids=surface_points.ids,
        ids_to_map=orientations.ids
    )
    poly['id'] = vectorize_ids
    poly['vectors'] = orientations_grads

    # Determine scaling mode
    if arrow_scale_mode == 'vector':
        # Scale arrows by their magnitude
        arrows = poly.glyph(
            orient='vectors',
            scale='vectors',
            factor=arrows_factor,
        )
    else:
        # Fixed scale (original behavior)
        arrows = poly.glyph(
            orient='vectors',
            scale=False,
            factor=arrows_factor,
        )

    # Optional: Add outlined arrows for better visibility
    if show_arrow_outline:
        # Create a slightly larger version for the outline
        arrows_outline = poly.glyph(
            orient='vectors',
            scale=False if arrow_scale_mode == 'fixed' else 'vectors',
            factor=arrows_factor 
        )
        
        # Add outline FIRST (behind)
        gempy_vista.p.add_mesh(
            mesh=arrows_outline,
            color=outline_color,
            style='wireframe',  # This is the key!
            line_width=outline_width,
            opacity=arrow_opacity,
        )

    # Add main colored arrows SECOND (in front)
    gempy_vista.orientations_actor = gempy_vista.p.add_mesh(
        mesh=arrows,
        scalars='id',
        show_scalar_bar=False,
        cmap=(ListedColormap(element_colors)),
        clim=(-0.5, np.unique(surface_points.ids).shape[0] + .5),
        opacity=arrow_opacity,
        smooth_shading=True,
    )
    gempy_vista.orientations_mesh = arrows

def _vectorize_ids(mapping_ids, ids_to_map):
    def _mapping_dict(ids):
        unique_values, first_indices = np.unique(ids, return_index=True)  # Find the unique elements and their first indices
        unique_values_order = unique_values[np.argsort(first_indices)]  # Sort the unique values by their first appearance in `a`
        # Flip order to please pyvista vertical scalarbar
        unique_values_order = unique_values_order[::-1]
        mapping_dict = {value: i + 1 for i, value in enumerate(unique_values_order)}  # Use a dictionary to map the original numbers to new values
        return mapping_dict

    mapping_dict = _mapping_dict(mapping_ids)

    # Filter out invalid IDs or provide a default value
    # Option 1: Filter out IDs that don't exist in mapping_dict
    valid_mask = np.isin(ids_to_map, list(mapping_dict.keys()))
    if not np.all(valid_mask):
        print(f"Warning: Found {np.sum(~valid_mask)} orientation IDs that don't exist in surface points. These will be assigned a default value of 0.")

    # Option 2: Use a default value (0) for missing IDs
    mapped_array = np.vectorize(lambda x: mapping_dict.get(x, 0))(ids_to_map)

    return mapped_array