import os
import pytest
import dotenv

import gempy as gp
from gempy.modules.serialization.save_load import load_model
from gempy_viewer import plot_3d

from tests.util_tests import check_image_hash

dotenv.load_dotenv()

@pytest.fixture(scope="module")
def model_path():
    path = os.getenv("PATH_TO_NUGGET_TEST_MODEL")
    if not path:
        pytest.skip("Environment variable PATH_TO_NUGGET_TEST_MODEL is not set")
    return path

@pytest.fixture
def geo_model(model_path):
    """Load the raw GemPy model from disk."""
    model_file = os.path.join(model_path, "nugget_effect_optimization.gempy")
    return load_model(model_file)

@pytest.fixture
def computed_model(geo_model):
    """Run gp.compute_model on the loaded model and return it."""
    gp.compute_model(
        gempy_model=geo_model,
        engine_config=gp.data.GemPyEngineConfig(
            backend=gp.data.AvailableBackends.numpy,
        ),
        validate_serialization=True,
    )
    return geo_model

class Test3DColormaps:
    def test_3d_volume_input(self, geo_model):
        """Simply plot without computing or data overlays."""
        plot3d = plot_3d(
            model=geo_model,
            image=True,
            show_data=True,
            show_topography=False,
            show_nugget_effect=True
        )

        check_image_hash(
            plot3d=plot3d,
            hash='07000019000'
        )

    def test_3d_volume_vol(self, computed_model):
        """Plot after compute_model, showing data."""
        plot3d = plot_3d(computed_model, image=True, show_data=True)

        check_image_hash(
            plot3d=plot3d,
            hash='070000b0000'
        )

    def test_3d_volume_mesh_and_data(self, computed_model):
        """Plot after compute_model, showing data but no lithology."""
        plot3d = plot_3d(computed_model, image=True, show_data=True, show_lith=False)

        check_image_hash(
            plot3d=plot3d,
            hash='06000030000'
        )
