import numpy as np

from gempy.core.data.structural_element import StructuralElement
from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from ...optional_dependencies import require_pyvista


def plot_surfaces(
        gempy_vista: GemPyToVista,
        structural_elements_with_solution: list[StructuralElement],
        **kwargs
):
    pv = require_pyvista()
    # ! If the order of the meshes does not match the order of scalar_field_at_surface points we need to reorder them in 'multi_scalar_dual_contouring.py'
    
    topography_mesh = gempy_vista.surface_poly.get('topography', None)
    
    for element in structural_elements_with_solution:
        vertices_ = element.vertices
        edges_ = element.edges
        if vertices_ is None or vertices_.shape[0] == 0 or edges_.shape[0] == 0:
            continue
        surf = pv.PolyData(vertices_, np.insert(edges_, 0, 3, axis=1).ravel())
        
        if topography_mesh is not None:
            surf = surf.clip_surface(topography_mesh, invert=True)
        
        gempy_vista.surface_poly[element.name] = surf
        gempy_vista.surface_actors[element.name] = gempy_vista.p.add_mesh(
            surf,
            pv.Color(element.color).float_rgb,
            show_scalar_bar=False,
            # cmap=cmap,
            **kwargs
        )
