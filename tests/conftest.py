import pytest
import numpy as np

from gempy import GeoModel, StackRelationType
import gempy as gp
from gempy.core.data.importer_helper import ImporterHelper


# TODO: Move this to gempy main repo
@pytest.fixture(scope='session')    
def one_fault_model_no_interp() -> GeoModel:
    data_path = 'https://raw.githubusercontent.com/cgre-aachen/gempy_data/master/'
    path_to_data = data_path + "/data/input_data/jan_models/"

    geo_data = gp.create_geomodel(
        project_name='fault',
        extent=[0, 1000, 0, 1000, 0, 1000],
        resolution=[50, 5, 50],
        importer_helper= ImporterHelper(
            path_to_surface_points=path_to_data + "model5_surface_points.csv",
            path_to_orientations=path_to_data + "model5_orientations.csv",
            hash_surface_points="8fe9250462c3e65080818a84d29925378664f6be46301dcdb42ed4047aa3fe6f",
            hash_orientations="58d1d28be0c52dfdcedf36c9adc3b231e67d6923554159d6484dba589b0bfc5e",
        )
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

    
