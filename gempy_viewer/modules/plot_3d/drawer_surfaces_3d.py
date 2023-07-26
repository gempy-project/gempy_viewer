from gempy_viewer.modules.plot_3d.vista import GemPyToVista
from gempy_engine.core.data.legacy_solutions import LegacySolution


def plot_surfaces(
        gempy_vista: GemPyToVista,
        solution: LegacySolution,
):
    raise NotImplementedError("We need to update this first.")
    select_active = surfaces_df['isActive']
    for idx, val in surfaces_df[select_active][['vertices', 'edges', 'color', 'surface', 'id']].dropna().iterrows():
        vertices_ = val['vertices']
        edges_ = val['edges']
        if isinstance(vertices_, list): vertices_ = vertices_[0]
        if isinstance(edges_, list): edges_ = edges_[0]

        if vertices_.shape[0] == 0 or edges_.shape[0] == 0:
            continue
        surf = pv.PolyData(vertices_, np.insert(edges_, 0, 3, axis=1).ravel())
        self.surface_poly[val['surface']] = surf
        self.surface_actors[val['surface']] = self.p.add_mesh(
            surf,
            pv.Color(val['color']).float_rgb,
            show_scalar_bar=True,
            cmap=cmap,
            **kwargs
        )
    self.set_bounds()

    # In order to set the scalar bar to only surfaces we would need to map
    # every vertex of each layer with the right id. So far I am going to avoid
    # the overhead since usually surfaces will be plotted either with data
    # or the regular grid.
    # self.set_scalar_bar()
    return self.surface_actors
