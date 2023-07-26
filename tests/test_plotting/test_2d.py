from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D
import matplotlib.pyplot as plt
import numpy as np
import pytest
import gempy_viewer as gpv
import gempy as gp

# TODO: - [x] Test sections
# TODO: - [x] Refactor plotting 2d
# TODO: - [ ] Refactor public and private methods


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
            show_section_traces=False, # TODO: Test this one
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
            d_z=np.array([600, 2000]),
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
            d_z=np.array([600, 2000]),
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
    def test_plot_2d_solutions_default(self, one_fault_model_topo_solution):
        _: Plot2D = gpv.plot_2d(one_fault_model_topo_solution)


    def test_plot_2d_all_together(self, one_fault_model_topo_solution):

        gpv.plot_2d(
            model=one_fault_model_topo_solution,
            section_names=['section_SW-NE', 'section_NW-SE', 'topography'],
            direction=['x', 'y', 'y'], cell_number=['mid', 'mid', 'mid'],
            show_lith=[False, False, False, True, True , True],
            show_boundaries=[False, False, False, True, True, True],
            show_scalar=[False, False, False, False, True, True],
            series_n=[0, 0, 0, 0, 0, 1],
            show_topography=True,
            show_section_traces=True  # TODO: Test this one
        )

    def test_ve(self, one_fault_model_topo_solution):
        raise NotImplementedError('Not implemented yet (TODO)')
        # Test ve
        p2d = gpv.plot_2d(one_fault_model_topo_solution, direction='x', cell_number='mid', show_topography=True, ve=3)

        plt.show()

