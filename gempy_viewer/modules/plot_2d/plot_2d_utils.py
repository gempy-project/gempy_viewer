from gempy.core.grid_modules import grid_types


def slice_cross_section(regular_grid: grid_types.RegularGrid, direction: str, cell_number=25):
    """
    Slice the 3D array (blocks or scalar field) in the specific direction selected in the plot functions

    """
    _a, _b, _c = (
        slice(0, regular_grid.resolution[0]),
        slice(0, regular_grid.resolution[1]),
        slice(0, regular_grid.resolution[2])
    )

    if direction == "x":
        cell_number = int(regular_grid.resolution[0] / 2) if cell_number == 'mid' else cell_number
        _a, x, y, Gx, Gy = cell_number, "Y", "Z", "G_y", "G_z"
        extent_val = regular_grid.extent[[2, 3, 4, 5]]
    elif direction == "y":
        cell_number = int(regular_grid.resolution[1] / 2) if cell_number == 'mid' else cell_number
        _b, x, y, Gx, Gy = cell_number, "X", "Z", "G_x", "G_z"
        extent_val = regular_grid.extent[[0, 1, 4, 5]]
    elif direction == "z":
        cell_number = int(regular_grid.resolution[2] / 2) if cell_number == 'mid' else cell_number
        _c, x, y, Gx, Gy = cell_number, "X", "Y", "G_x", "G_y"
        extent_val = regular_grid.extent[[0, 1, 2, 3]]
    else:
        raise AttributeError(str(direction) + "must be a cartesian direction, i.e. xyz")
    return _a, _b, _c, extent_val, x, y, Gx, Gy
