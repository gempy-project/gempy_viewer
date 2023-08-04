import matplotlib.pyplot as plt
import numpy as np

from gempy.core.data import GeoModel
from gempy_viewer.core.data_to_show import DataToShow
from gempy_viewer.core.scalar_data_type import ScalarDataType, TopographyDataType
from gempy_viewer.modules.plot_2d.plot_2d_utils import get_geo_model_cmap
from gempy_viewer.modules.plot_3d.drawer_input_3d import plot_data
from gempy_viewer.modules.plot_3d.drawer_structured_grid_3d import plot_structured_grid
from gempy_viewer.modules.plot_3d.drawer_surfaces_3d import plot_surfaces
from gempy_viewer.modules.plot_3d.drawer_topography_3d import plot_topography_3d
from gempy_viewer.modules.plot_3d.plot_3d_utils import set_scalar_bar
from gempy_viewer.modules.plot_3d.vista import GemPyToVista

try:
    import pyvista as pv
    from gempy_viewer.modules.plot_3d._vista import Vista as Vista

    PYVISTA_IMPORT = True
except ImportError:
    PYVISTA_IMPORT = False

try:
    import mplstereonet

    mplstereonet_import = True
except ImportError:
    mplstereonet_import = False


def plot_3d(
        model: GeoModel,
        plotter_type='basic',
        active_scalar_field: str = None,
        ve=None,
        topography_scalar_type: TopographyDataType = TopographyDataType.GEOMAP,
        kwargs_plot_structured_grid=None,
        kwargs_plot_topography=None,
        kwargs_plot_data=None,
        kwargs_plotter=None,
        kwargs_plot_surfaces=None,
        image=False,
        off_screen=False,
        **kwargs
) -> GemPyToVista:
    """Plot 3-D geomodel."""
    # * Grab from kwargs all the show arguments and create the proper class. This is for backwards compatibility
    can_show_results = model.solutions is not None  # and model.solutions.lith_block.shape[0] != 0
    data_to_show = DataToShow(
        n_axis=1,
        show_data=kwargs.get('show_data', True),
        show_results=kwargs.get('show_results', can_show_results),
        show_surfaces=kwargs.get('show_surfaces', True),
        show_lith=kwargs.get('show_lith', True),
        show_scalar=kwargs.get('show_scalar', False),
        show_boundaries=kwargs.get('show_boundaries', True),
        show_topography=kwargs.get('show_topography', True),
        show_section_traces=kwargs.get('show_section_traces', True),
        show_values=kwargs.get('show_values', False),
        show_block=kwargs.get('show_block', False)
    )
    kwargs_plot_topography = kwargs_plot_topography or {}
    kwargs_plot_structured_grid = kwargs_plot_structured_grid or {}
    kwargs_plot_data = kwargs_plot_data or {}
    kwargs_plotter = kwargs_plotter or {}
    kwargs_plot_surfaces = kwargs_plot_surfaces or {}

    if image is True:
        off_screen = True
        kwargs_plotter['off_screen'] = True
        plotter_type = 'basic'

   
    extent: np.ndarray = model.grid.regular_grid.extent

    gempy_vista = GemPyToVista(
        extent=extent,
        plotter_type=plotter_type,
        **kwargs_plotter
    )

    if data_to_show.show_topography[0] is True and model.grid.topography is not None:
        plot_topography_3d(
            gempy_vista=gempy_vista,
            topography=model.grid.topography,
            solution=model.solutions.raw_arrays,
            topography_scalar_type=topography_scalar_type,
            elements_colors=model.structural_frame.elements_colors_contacts,
            contours=kwargs_plot_topography.get('contours', True),
            **kwargs_plot_topography
        )
        
    if data_to_show.show_boundaries[0] is True and len(model.solutions.raw_arrays.vertices) != 0:
        plot_surfaces(
            gempy_vista=gempy_vista,
            structural_elements_with_solution=model.structural_frame.structural_elements,
            **kwargs_plot_surfaces
        )

    if data_to_show.show_lith[0] is True:
        plot_structured_grid(
            gempy_vista=gempy_vista,
            regular_grid=model.grid.regular_grid,
            scalar_data_type=ScalarDataType.LITHOLOGY,
            active_scalar_field="lith",
            solution=model.solutions.raw_arrays,
            cmap=get_geo_model_cmap(model.structural_frame.elements_colors_volumes),
            **kwargs_plot_structured_grid
        )

    if data_to_show.show_scalar[0] is True:
        plot_structured_grid(
            gempy_vista=gempy_vista,
            regular_grid=model.grid.regular_grid,
            scalar_data_type=ScalarDataType.SCALAR_FIELD,
            active_scalar_field=active_scalar_field,
            solution=model.solutions.raw_arrays,
            cmap='viridis',
            **kwargs_plot_structured_grid
        )

    if data_to_show.show_data[0] is True:
        arrow_size = kwargs.get('arrow_size', 10)
        min_axes = np.min(np.diff(extent)[[0, 2, 4]])

        plot_data(
            gempy_vista=gempy_vista,
            surface_points=model.structural_frame.surface_points,
            orientations=model.structural_frame.orientations,
            arrows_factor=arrow_size / (100 / min_axes),
            elements_colors=model.structural_frame.elements_colors_contacts[:-1],
            **kwargs_plot_data
        )

    
    # set_scalar_bar(
    #     gempy_vista=gempy_vista,
    #     n_labels=model.structural_frame.number_of_elements,
    #     surfaces_ids=model.structural_frame.elements_ids - 1
    # )

    if ve is not None:
        gempy_vista.p.set_scale(zscale=ve)

    fig_path: str = kwargs.get('fig_path', None)
    if fig_path is not None:
        gempy_vista.p.show(screenshot=fig_path)

    if image is True:
        gempy_vista.p.show(screenshot=True)
        img = gempy_vista.p.last_image
        plt.imshow(img)
        plt.axis('off')
        plt.show(block=False)
        gempy_vista.p.close()

    if off_screen is False:
        gempy_vista.p.show()

    return gempy_vista
