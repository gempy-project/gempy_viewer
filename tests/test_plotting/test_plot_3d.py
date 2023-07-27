import gempy_viewer as gpv
from gempy_viewer.core.scalar_data_type import TopographyDataType


class TestPlot3dInputData:
    def test_plot_3d_input_data(self, one_fault_model_no_interp):
        gpv.plot_3d(one_fault_model_no_interp)


class TestPlot3DSolutions:
    def test_plot_3d_solutions_default(self, one_fault_model_topo_solution):
        gpv.plot_3d(one_fault_model_topo_solution)
    
    def test_plot_3d_solutions(self, one_fault_model_topo_solution):
        gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_scalar=False,
            show_lith=False,
            show_data=True,
            show_boundaries=True
        )
    
    def test_plot_3d_scalar_field(self, one_fault_model_topo_solution):
        gpv.plot_3d(
            model=one_fault_model_topo_solution,
            active_scalar_field="sf_1",
            show_scalar=True,
            show_lith=False
        )
    
    def test_plot_3d_solutions_topography(self, one_fault_model_topo_solution):
        gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=True,
            topography_scalar_type=TopographyDataType.TOPOGRAPHY
        )
    
    def test_plot_3d_solutions_topography_geological_map(self, one_fault_model_topo_solution):
        raise NotImplementedError("We need to interpolate the geological map first.")
        gpv.plot_3d(
            model=one_fault_model_topo_solution,
            show_topography=True,
            topography_scalar_type=TopographyDataType.GEOMAP
        )