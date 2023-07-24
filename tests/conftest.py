import pytest
import numpy as np

from gempy import GeoModel, StackRelationType
import gempy as gp


@pytest.fixture(scope='session')
def one_fault_model_no_interp() -> GeoModel:
    data_path = 'https://raw.githubusercontent.com/cgre-aachen/gempy_data/master/'
    path_to_data = data_path + "/data/input_data/jan_models/"

    geo_data = gp.create_data_legacy(
        project_name='fault',
        extent=[0, 1000, 0, 1000, 0, 1000],
        resolution=[50, 50, 50],
        path_o=path_to_data + "model5_orientations.csv",
        path_i=path_to_data + "model5_surface_points.csv"
    )

    # %%
    # Setting and ordering the units and series:
    # 
    gp.map_stack_to_surfaces(
        geo_data,
        {
            "Fault_Series": 'fault',
            "Strat_Series": ('rock2', 'rock1')
        }
    )

    # %%
    # Define fault groups
    # TODO: Abstract this away with the old set_fault method
    geo_data.structural_frame.structural_groups[0].structural_relation = StackRelationType.FAULT
    geo_data.structural_frame.fault_relations = np.array([[0, 1], [0, 0]])
    
    return geo_data

    
