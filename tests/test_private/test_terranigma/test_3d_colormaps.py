import os

import dotenv
import gempy as gp
from gempy.modules.serialization.save_load import load_model
from gempy_viewer import plot_3d

dotenv.load_dotenv()

path = os.getenv("PATH_TO_NUGGET_TEST_MODEL")

def test_3d_volume_input():
    geo_model: gp.data.GeoModel = load_model(path + "/nugget_effect_optimization.gempy")

    plot_3d(
        geo_model,
        image=False,
    )

def test_3d_volume_vol():
    geo_model:gp.data.GeoModel = load_model(path + "/nugget_effect_optimization.gempy")
    print(geo_model)
    gp.compute_model(
        gempy_model=geo_model,
        engine_config=gp.data.GemPyEngineConfig(
            backend=gp.data.AvailableBackends.PYTORCH,
        ),
        validate_serialization=True
    )

    plot_3d(
        geo_model, 
        image=False, 
        show_data=False
    )
    pass


def test_3d_volume_mesh():
    geo_model: gp.data.GeoModel = load_model(path + "/nugget_effect_optimization.gempy")
    print(geo_model)
    gp.compute_model(
        gempy_model=geo_model,
        engine_config=gp.data.GemPyEngineConfig(
            backend=gp.data.AvailableBackends.PYTORCH,
        ),
        validate_serialization=True
    )

    plot_3d(
        geo_model,
        image=False,
        show_data=False,
        show_lith=False
    )


def test_3d_orientations():
    pass