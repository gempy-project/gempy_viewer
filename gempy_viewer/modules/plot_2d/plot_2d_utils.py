import numpy as np

from gempy.core.grid_modules import grid_types
from gempy.core.grid_modules.grid_types import Sections


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


def make_section_xylabels(sections: Sections, section_name, n=5):
    """
    @elisa heim
    Setting the axis labels to any combination of vertical crossections

    Args:
        section_name: name of a defined gempy crossection. See gempy.Model().grid.section
        n:

    Returns:

    """
    if n > 5:
        n = 3  # todo I don't know why but sometimes it wants to make a lot of xticks
    elif n < 0:
        n = 3

    j = np.where(sections.names == section_name)[0][0]
    startend = list(sections.section_dict.values())[j]
    p1, p2 = startend[0], startend[1]
    xy = sections.calculate_line_coordinates_2points(p1, p2, n)
    if len(np.unique(xy[:, 0])) == 1:
        labels = xy[:, 1].astype(int)
        axname = 'Y'
    elif len(np.unique(xy[:, 1])) == 1:
        labels = xy[:, 0].astype(int)
        axname = 'X'
    else:
        labels = [str(xy[:, 0].astype(int)[i]) + ',\n' + str(xy[:, 1].astype(int)[i]) for i in
                  range(xy[:, 0].shape[0])]
        axname = 'X,Y'
    return labels, axname
