import pytest


@pytest.mark.skipif(True, "Run explicitly to test installation")
def test_pyvista():
    import pyvista

    mesh = pyvista.Sphere()
    mesh.plot()
