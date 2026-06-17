"""Verify the volume element properties and ID remapping work correctly."""
import numpy as np
from gempy.core.data import GeoModel


def test_volume_elements_properties(one_fault_model_topo_solution: GeoModel):
    sf = one_fault_model_topo_solution.structural_frame

    vol_elems = sf.volume_elements
    vol_names = sf.volume_elements_names
    vol_colors = sf.volume_elements_colors
    vol_enum = sf.volume_elements_enumerator

    print("\n=== Volume elements ===")
    print("volume_elements:", [e.name for e in vol_elems])
    print("volume_names:", vol_names)
    print("volume_colors:", vol_colors)
    print("volume_enumerator:", vol_enum)

    assert len(vol_elems) == 3
    assert vol_names == ['rock2', 'rock1', 'basement']
    assert len(vol_colors) == 3
    assert np.array_equal(vol_enum, np.array([1, 2, 3]))
    assert 'fault' not in vol_names
    assert 'fault' in sf.elements_names


def test_lith_block_remapping(one_fault_model_topo_solution: GeoModel):
    raw = one_fault_model_topo_solution.solutions.raw_arrays

    unique_vals = np.sort(np.unique(raw.lith_block))
    lith_to_id = {int(v): i + 1 for i, v in enumerate(unique_vals)}
    block_ = np.array([lith_to_id[int(v)] for v in raw.lith_block.ravel()])

    print("\n=== ID Remapping ===")
    print("lith_block unique:", unique_vals)
    print("mapping:", lith_to_id)
    print("remapped unique:", np.unique(block_))

    assert np.array_equal(unique_vals, np.array([2, 3, 4]))
    assert lith_to_id == {2: 1, 3: 2, 4: 3}
    assert np.array_equal(np.unique(block_), np.array([1, 2, 3]))
