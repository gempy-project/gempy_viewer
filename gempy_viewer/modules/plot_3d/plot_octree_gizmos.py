from numpy import ndarray

from gempy.core.data import GeoModel
from gempy_viewer import GemPyToVista


def plot_octree_gizmos(model: GeoModel, pd3: GemPyToVista):
    import matplotlib.pyplot as plt
    octree_outputs = model.solutions.octrees_output
    n_levels = len(octree_outputs)
    cmap = plt.get_cmap('viridis')

    for i, octree_level in enumerate(octree_outputs):
        # Map the current level (i) to a 0.0 - 1.0 range for the colormap
        level_color = cmap(i / max(1, n_levels - 1))[:3]

        _plot_octree_gizmos(
            model=model,
            numbers=octree_level.grid_centers.corners_grid.values,
            pd3=pd3,
            color=level_color
        )


def _plot_octree_gizmos(model: GeoModel, numbers: ndarray, pd3: GemPyToVista, color):
    import pyvista as pv
    import numpy as np

    world_coord_vertices = model.input_transform.apply_inverse(numbers)
    numbers = model.grid.transform.apply_inverse_with_cached_pivot(world_coord_vertices)
    # 1. Reshape to (N_boxes, 8, 3)
    n_boxes = numbers.shape[0] // 8
    nodes = numbers.reshape(n_boxes * 8, 3)

    # 2. Define the connectivity for PyVista HEXAHEDRON
    # GemPy generation order (X slowest, Z fastest): 
    # 0:000, 1:001, 2:010, 3:011, 4:100, 5:101, 6:110, 7:111
    # VTK Hexahedron order:
    # Bottom face: 000, 100, 110, 010 (indices: 0, 4, 6, 2)
    # Top face:    001, 101, 111, 011 (indices: 1, 5, 7, 3)

    permutation = np.array([0, 4, 6, 2, 1, 5, 7, 3])

    # Create the base indices and apply permutation
    base_indices = np.arange(n_boxes * 8).reshape(n_boxes, 8)
    reordered_indices = base_indices[:, permutation]

    cells = np.hstack([
            np.full((n_boxes, 1), 8),
            reordered_indices
    ]).ravel()

    cell_types = np.full(n_boxes, pv.CellType.HEXAHEDRON, dtype=np.uint8)

    # 3. Create the UnstructuredGrid
    # This is much more robust than glyphing centers because it uses the actual corners
    grid = pv.UnstructuredGrid(cells, cell_types, nodes)

    # 4. Extract only the edges (wireframe)
    edges = grid.extract_all_edges()

    pd3.p.add_mesh(edges, show_edges=True, color=color, opacity=0.3, line_width=1)
