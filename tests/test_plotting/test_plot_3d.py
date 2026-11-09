import numpy as np
import pytest

import gempy_viewer as gpv
import gempy as gp
from gempy.core.data import GeoModel
from gempy_viewer.core.scalar_data_type import TopographyDataType
from tests.util_tests import check_image_hash
from tests.conftest import _one_fault_model_generator

np.random.seed(1234)


class TestPlot3dInputData:
    def test_plot_3d_input_data(self, one_fault_model_no_interp):
        gpv.plot_3d(one_fault_model_no_interp, image=True)


class TestPlot3DSolutions:
    def test_plot_3d_solutions_default(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        gpv.plot_3d(one_fault_model_topo_solution, image=True)
        

    def test_plot_3d_solutions(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        plot3d = gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=True,
            show_scalar=False,
            show_lith=True,
            show_data=True,
            show_boundaries=True,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07040030001'
        )

    def test_plot_3d_solutions_volume_and_input(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        plot3d = gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=False,
            show_scalar=False,
            show_lith=True,
            show_data=True,
            show_boundaries=True,
            image=True,
            kwargs_plot_structured_grid = {'opacity': 0.5}
        )


        check_image_hash(
            plot3d=plot3d,
            hash='07400018000'
        )

    def test_plot_3d_solutions_only_volume(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        plot3d =gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=False,
            show_scalar=False,
            show_lith=True,
            show_data=False,
            show_boundaries=False,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07c00000000'
        )

    def test_plot_3d_solutions_only_input(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        plot3d =gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=False,
            show_scalar=False,
            show_lith=False,
            show_data=True,
            show_boundaries=True,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='06000038040'
        )

    def test_plot_3d_scalar_field(self, one_fault_model_topo_solution):
        plot3d = gpv.plot_3d(
            model=one_fault_model_topo_solution,
            active_scalar_field="sf_1",
            show_scalar=True,
            show_lith=False,
            show_topography=False,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07600210000'
        )

    def test_plot_3d_solutions_topography(self, one_fault_model_topo_solution):
        plot3d =gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=True,
            topography_scalar_type=TopographyDataType.TOPOGRAPHY,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07440001000'
        )

    def test_plot_3d_solutions_topography_geological_map(self, one_fault_model_topo_solution):
        plot3d =gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_lith=True,
            show_topography=True,
            topography_scalar_type=TopographyDataType.GEOMAP,
            image=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07040030001'
        )


class TestPlot2DSolutionsOctrees:
    @pytest.fixture(scope='class')
    def one_fault_model_topo_solution_octrees(self) -> GeoModel:
        one_fault_model = _one_fault_model_generator()
        one_fault_model.grid.regular_grid.set_regular_grid(
            extent=one_fault_model.grid.regular_grid.extent,
            resolution=np.array([2, 4, 2])
        )

        one_fault_model.interpolation_options.number_octree_levels = 5

        # TODO: Test octree regular grid with everything else combined
        gp.set_section_grid(
            grid=one_fault_model.grid,
            section_dict={'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                          'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}
        )

        gp.set_topography_from_random(
            grid=one_fault_model.grid,
            fractal_dimension=1.2,
            d_z=np.array([600, 2000]),
            topography_resolution=np.array([60, 60])
        )

        gp.compute_model(one_fault_model)
        return one_fault_model

    def test_plot_3d_solutions_default(self, one_fault_model_topo_solution_octrees):
        gpv.plot_3d(one_fault_model_topo_solution_octrees, image=True)


class TestPlot3DThinModelTopography:
    """Regression: the lithology volume used to be clipped a fixed 10 model units below
    the topography, which removed most of the volume in thin models."""

    @pytest.fixture(scope='class')
    def thin_model(self) -> GeoModel:
        rng_state = np.random.get_state()
        np.random.seed(1234)
        geo_model = gp.create_geomodel(
            project_name='thin_model',
            extent=[0, 100, 0, 100, 0, 20],
            resolution=[10, 10, 10],
            structural_frame=gp.data.StructuralFrame.from_data_tables(
                surface_points=gp.data.SurfacePointsTable.from_arrays(
                    x=np.array([10., 50., 90., 50.]), y=np.array([50., 10., 50., 90.]),
                    z=np.array([8., 8., 8., 8.]), names='layer'
                ),
                orientations=gp.data.OrientationsTable.from_arrays(
                    x=np.array([50.]), y=np.array([50.]), z=np.array([8.]),
                    G_x=np.array([0.]), G_y=np.array([0.]), G_z=np.array([1.]), names='layer'
                )
            )
        )
        gp.set_topography_from_random(
            grid=geo_model.grid,
            fractal_dimension=1.2,
            d_z=np.array([12, 20]),
            topography_resolution=np.array([20, 20])
        )
        np.random.set_state(rng_state)
        gp.compute_model(geo_model)
        return geo_model

    def test_lith_volume_reaches_topography(self, thin_model):
        plot3d = gpv.plot_3d(thin_model, show_topography=True, show_lith=True, show=False,
                             kwargs_plotter={'off_screen': True})
        volume_z_max = plot3d.regular_grid_actor.mapper.dataset.bounds[5]
        topography_z_min = thin_model.grid.topography.values[:, 2].min()
        # With the old fixed offset the volume ended ~10 units below the topography (z <= 10)
        assert volume_z_max >= topography_z_min
        plot3d.p.close()
