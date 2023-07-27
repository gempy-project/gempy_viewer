import pyvista as pv
import numpy as np

from gempy.core.data.structural_element import StructuralElement
from gempy_viewer.modules.plot_3d.vista import GemPyToVista



def plot_surfaces(
        gempy_vista: GemPyToVista,
        structural_elements_with_solution: list[StructuralElement],
        **kwargs
):
    for element in structural_elements_with_solution:
        vertices_ = element.vertices
        edges_ = element.edges
        if vertices_ is None or vertices_.shape[0] == 0 or edges_.shape[0] == 0:
            continue
        surf = pv.PolyData(vertices_, np.insert(edges_, 0, 3, axis=1).ravel())
        gempy_vista.surface_poly[element.name] = surf
        gempy_vista.surface_actors[element.name] = gempy_vista.p.add_mesh(
            surf,
            pv.Color(element.color).float_rgb,
            show_scalar_bar=True,
            # cmap=cmap,
            **kwargs
        )
