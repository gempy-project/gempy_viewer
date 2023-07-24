from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D
import matplotlib.pyplot as plt
import numpy as np
import pytest
import gempy_viewer as gpv
import gempy as gp

# TODO: - [ ] Test sections
# TODO: - [ ] Refactor plotting 2d


class TestPlot2DInputData:
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
            show_section_traces=False, # TODO: Test this one
            projection_distance=1000,
        )
    
    def test_plot_2d_topography(self, one_fault_model_no_interp):
        raise NotImplementedError
    
    def test_plot_2d_test_labels(self, one_fault_model_no_interp):
        geo_model = one_fault_model_no_interp
        section_dict = {'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                        'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}
        geo_model.set_section_grid(section_dict)
        geo_model.set_topography(fd=1.2, d_z=np.array([600, 2000]), resolution=np.array([60, 60]))

        gp.plot_2d(
            model=geo_model,
            section_names=['section_NW-SE', 'section_NW-SE', 'topography'],
            direction=['x'], cell_number=['mid'],
            show_topography=True,
            show_section_traces=True
        )
        plt.show()

        gp.plot_2d(geo_model,
                   section_names=['section_NW-SE', 'section_NW-SE', 'topography'],
                   direction=['x'], cell_number=['mid'],
                   show_topography=True,
                   projection_distance=100)
        plt.show()

        gp.plot_2d(geo_model,
                   section_names=['section_NW-SE', 'section_NW-SE', 'topography'],
                   direction=['x'], cell_number=['mid'],
                   show_topography=True,
                   projection_distance=1000)
        plt.show()

        # gp.plot.plot_section_traces(geo_model)
        plt.show()


class TestPlot2DSolutions:
    @pytest.fixture(scope='module')
    def section_model(self, one_fault_model_topo_solution):
        geo_model = one_fault_model_topo_solution
        section_dict = {'section_SW-NE': ([250, 250], [1750, 1750], [100, 100]),
                        'section_NW-SE': ([250, 1750], [1750, 250], [100, 100])}
        geo_model.set_section_grid(section_dict)

        geo_model.set_active_grid('sections', reset=False)

        one_fault_model_topo_solution.update_additional_data()
        one_fault_model_topo_solution.update_to_interpolator()
        gp.compute_model(geo_model, sort_surfaces=False)
        return geo_model

    def test_topo_sections_iterp2(self, section_model):
        # Test 1 single
        gp.plot_2d(section_model, section_names=['section_NW-SE'],
                   show_topography=True)
        plt.show()

        # Test 2 plots
        gp.plot_2d(section_model, section_names=['section_NW-SE', 'section_NW-SE'],
                   show_topography=True)
        plt.show()

        # Test 3 plots
        gp.plot_2d(section_model, section_names=['section_NW-SE', 'section_NW-SE', 'topography'],
                   show_topography=True)
        plt.show()

        # Test 4
        gp.plot_2d(section_model, section_names=['section_NW-SE', 'section_NW-SE', 'topography'],
                   direction=['x'], cell_number=['mid'],
                   show_topography=True)
        plt.show()

        gp.plot.plot_section_traces(section_model)
        plt.show()

    def test_show_results(self, section_model):
        p2d = gp.plot_2d(section_model,
                         show_data=False,
                         show_topography=False,
                         show_results=True,
                         show=True)

    def test_ve(self, section_model):
        # Test ve
        p2d = gp.plot_2d(section_model, section_names=['section_NW-SE', 'section_NW-SE'],
                         show_topography=True, ve=3)

        plt.show()

    def test_topo_resize(self, one_fault_model_topo_solution):
        geo_model = one_fault_model_topo_solution
        geo_model.set_topography(fd=1.2, d_z=np.array([600, 2000]), resolution=np.array([60, 60]))
        sol = gp.compute_model(geo_model, compute_mesh=False)
        gp.plot_2d(geo_model, section_names=['topography'])
        plt.show()
