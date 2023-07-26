import gempy_viewer as gpv


class TestPlot3dInputData:
    def test_plot_3d_input_data(self, one_fault_model_no_interp):
        gpv.plot_3d(one_fault_model_no_interp)


class TestPlot3DSolutions:
    def test_plot_3d_solutions_default(self, one_fault_model_topo_solution):
        gpv.plot_3d(one_fault_model_topo_solution)
    
    def test_plot_3d_scalar_field(self, one_fault_model_topo_solution):
        gpv.plot_3d(
            model=one_fault_model_topo_solution,
            active_scalar_field="sf_1",
            show_scalar=True,
            show_lith=False
        )