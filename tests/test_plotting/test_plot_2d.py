from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np
import pytest

import gempy as gp
import gempy_viewer as gpv
from gempy_viewer.modules.plot_2d import drawer_contours_2d
from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D
from tests.conftest import _one_fault_model_generator


# TODO: - [x] Test sections
# TODO: - [x] Refactor plotting 2d
# TODO: - [ ] Refactor public and private methods


class TestPlot2DInputData:
    @pytest.fixture(scope='class')
    def one_fault_model_no_interp(self) -> gp.data.GeoModel:
        geo_data = _one_fault_model_generator()
        return geo_data

    def test_plot_2d_data_default(self, one_fault_model_no_interp):
        _: Plot2D = gpv.plot_2d(one_fault_model_no_interp)

    def test_plot_2d_data_default_all_none(self, one_fault_model_no_interp):
        gpv.plot_2d(one_fault_model_no_interp, show_data=True, show_results=False)

    def test_plot_2d_data_cross_section(self, one_fault_model_no_interp):
        geo_model = one_fault_model_no_interp
        section_dict = {'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                        'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}

        gp.set_section_grid(
            grid=geo_model.grid,
            section_dict=section_dict
        )

        gpv.plot_2d(
            model=geo_model,
            section_names=['section_SW-NE', 'section_NW-SE'],
            show_section_traces=False,  # TODO: Test this one
        )

    def test_plot_2d_topography(self, one_fault_model_no_interp):
        gp.set_topography_from_random(
            grid=one_fault_model_no_interp.grid,
            fractal_dimension=1.2,
            d_z=np.array([600, 2000]),
            topography_resolution=np.array([60, 60])
        )

        gpv.plot_2d(
            model=one_fault_model_no_interp,
            section_names=['topography'],
            show_topography=True,
            show_section_traces=False,  # TODO: Test this one
        )

    def test_plot_2d_topography_and_sections(self, one_fault_model_no_interp):
        gp.set_section_grid(
            grid=one_fault_model_no_interp.grid,
            section_dict={'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                          'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}
        )

        gp.set_topography_from_random(
            grid=one_fault_model_no_interp.grid,
            fractal_dimension=1.2,
            d_z=np.array([600, 1000]),
            topography_resolution=np.array([60, 60])
        )

        gpv.plot_2d(
            model=one_fault_model_no_interp,
            section_names=['section_SW-NE', 'section_NW-SE', 'topography'],
            show_topography=True,
            show_section_traces=True  # TODO: Test this one
        )

    def test_plot_2d_all_together(self, one_fault_model_no_interp):
        gp.set_section_grid(
            grid=one_fault_model_no_interp.grid,
            section_dict={'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                          'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}
        )

        gp.set_topography_from_random(
            grid=one_fault_model_no_interp.grid,
            fractal_dimension=1.2,
            d_z=np.array([600, 1000]),
            topography_resolution=np.array([60, 60])
        )

        gpv.plot_2d(
            model=one_fault_model_no_interp,
            section_names=['section_SW-NE', 'section_NW-SE', 'topography'],
            direction=['x'], cell_number=['mid'],
            show_topography=True,
            show_section_traces=True  # TODO: Test this one
        )


class TestPlot2DSolutions:
    @pytest.fixture(scope='class')
    def one_fault_model_topo_solution(self) -> gp.data.GeoModel:
        one_fault_model = _one_fault_model_generator()

        gp.set_section_grid(
            grid=one_fault_model.grid,
            section_dict={'section_SW-NE': ([250, 250], [250, 1750], [50, 50]),
                          'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])
                          }
        )

        gp.set_topography_from_random(
            grid=one_fault_model.grid,
            fractal_dimension=1.8,
            d_z=np.array([600, 2000]),
            topography_resolution=np.array([60, 60])
        )

        gp.compute_model(one_fault_model)
        return one_fault_model

    def test_plot_2d_solutions_default(self, one_fault_model_topo_solution):
        print(one_fault_model_topo_solution.structural_frame)
        _: Plot2D = gpv.plot_2d(one_fault_model_topo_solution)

    def test_plot_2d_section(self, one_fault_model_topo_solution):
        _: Plot2D = gpv.plot_2d(
            model=one_fault_model_topo_solution,
            section_names=['section_SW-NE'],
            show_boundaries=True,
            show_topography=True
        )

    def test_plot_section_contacts_converts_torch_image_to_numpy(self, monkeypatch):
        torch = pytest.importorskip('torch')
        torch_image = torch.ones((2, 2), device='cuda' if torch.cuda.is_available() else 'cpu')
        contour_images = []
        gempy_model = SimpleNamespace(
            solutions=SimpleNamespace(
                raw_arrays=SimpleNamespace(
                    scalar_field_matrix=[np.zeros(4)],
                    scalar_field_at_surface_points=[np.array([1.0])]
                )
            ),
            structural_frame=SimpleNamespace(elements_colors_contacts=np.array(['red']))
        )

        monkeypatch.setattr(drawer_contours_2d, '_prepare_section_image', lambda *args, **kwargs: torch_image)
        monkeypatch.setattr(
            drawer_contours_2d.BackendTensor.t,
            'to_numpy',
            lambda tensor: tensor.cpu().detach().numpy()
        )

        fig, ax = plt.subplots()
        monkeypatch.setattr(ax, 'contour', lambda image, *args, **kwargs: contour_images.append(image))

        drawer_contours_2d.plot_section_contacts(
            gempy_model=gempy_model,
            ax=ax,
            section_name='section_SW-NE'
        )

        assert contour_images
        assert all(isinstance(image, np.ndarray) for image in contour_images)
        plt.close(fig)

    def test_plot_2d_all_together(self, one_fault_model_topo_solution):
        gpv.plot_2d(
            model=one_fault_model_topo_solution,
            section_names=['section_SW-NE', 'section_NW-SE', 'topography'],
            direction=['x', 'y', 'y'], cell_number=['mid', 'mid', 'mid'],
            show_lith=[False, False, True, True, True, True],
            show_boundaries=[False, False, False, True, True, True],
            show_scalar=[False, False, False, False, True, True],
            series_n=[0, 0, 0, 0, 0, 1],
            show_topography=True,
            show_section_traces=True  # TODO: Test this one
        )

    def test_plot_2d_topography_z_direction(self, one_fault_model_topo_solution):
        # Regression test for https://github.com/gempy-project/gempy/issues/1088:
        # show_topography used to only mask 'x'/'y' orthogonal cuts, raising
        # NotImplementedError for a fixed-Z ('z' direction) cut.
        gpv.plot_2d(
            model=one_fault_model_topo_solution,
            direction=['z'],
            cell_number=['mid'],
            show_topography=True
        )

    def test_plot_2d_position(self, one_fault_model_topo_solution):
        # Regression test for https://github.com/gempy-project/gempy/issues/882: slice by a
        # real-world coordinate instead of having to work out the matching cell_number.
        regular_grid = one_fault_model_topo_solution.grid.regular_grid
        p2d = gpv.plot_2d(
            model=one_fault_model_topo_solution,
            position=[500, 750],
            direction=['x', 'y'],
            show=False
        )
        expected_x = int(round((500 - regular_grid.extent[0]) / regular_grid.dx))
        expected_y = int(round((750 - regular_grid.extent[2]) / regular_grid.dy))
        assert p2d.axes[0].cell_number == expected_x
        assert p2d.axes[1].cell_number == expected_y

    def test_plot_2d_position_and_cell_number_mutually_exclusive(self, one_fault_model_topo_solution):
        with pytest.raises(ValueError):
            gpv.plot_2d(
                model=one_fault_model_topo_solution,
                position=[500],
                cell_number=['mid'],
                show=False
            )

    def test_plot_2d_position_out_of_extent_clamps_with_warning(self, one_fault_model_topo_solution):
        regular_grid = one_fault_model_topo_solution.grid.regular_grid
        with pytest.warns(UserWarning, match="outside the model extent"):
            p2d = gpv.plot_2d(
                model=one_fault_model_topo_solution,
                position=999_999,
                direction='x',
                show=False
            )
        assert p2d.axes[0].cell_number == regular_grid.resolution[0] - 1

    def test_ve(self, one_fault_model_topo_solution):
        # Test ve
        p2d = gpv.plot_2d(one_fault_model_topo_solution, direction='x', cell_number='mid',
                          show_topography=True, ve=1)

        plt.show()


class TestPlot2DSolutionsOctrees:
    @pytest.fixture(scope='class')
    def one_fault_model_topo_solution_octrees(self) -> gp.data.GeoModel:
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
            d_z=np.array([600, 1000]),
            topography_resolution=np.array([60, 60])
        )

        gp.compute_model(one_fault_model)
        return one_fault_model

    def test_plot_2d_solutions_default(self, one_fault_model_topo_solution_octrees):
        print(one_fault_model_topo_solution_octrees.structural_frame)
        _: Plot2D = gpv.plot_2d(
            model=one_fault_model_topo_solution_octrees,
            show_boundaries=True
        )

    def test_plot_2d_solutions_scalar(self, one_fault_model_topo_solution_octrees):
        print(one_fault_model_topo_solution_octrees.structural_frame)
        _: Plot2D = gpv.plot_2d(
            model=one_fault_model_topo_solution_octrees,
            show_boundaries=False,
            show_scalar=True,
            series_n=1
        )

    def test_plot_2d_all_together(self, one_fault_model_topo_solution_octrees):
        gpv.plot_2d(
            model=one_fault_model_topo_solution_octrees,
            section_names=['section_SW-NE', 'section_NW-SE', 'topography'],
            direction=['x', 'y', 'y'], cell_number=['mid', 'mid', 'mid'],
            show_lith=[False, False, False, True, True, True],
            show_boundaries=[False, False, False, True, True, True],
            show_scalar=[False, False, False, False, True, True],
            series_n=[0, 0, 0, 0, 0, 1],
            show_topography=True,
            show_section_traces=True  # TODO: Test this one
        )
