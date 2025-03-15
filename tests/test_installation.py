import pytest


@pytest.mark.skipif("Run explicitly to test installation")
def test_pyvista():
    import pyvista

    mesh = pyvista.Sphere()
    mesh.plot()
