from typing import Union

import numpy as np
import pandas as pd

from gempy_viewer.modules.plot_3d.vista import GemPyToVista


# ? Is this used?
def select_surfaces_data(data_df: pd.DataFrame, surfaces: Union[str, list[str]] = 'all') -> pd.DataFrame:
    """Select the surfaces that has to be plot.

    Args:
        data_df (pd.core.frame.DataFrame): GemPy data df that contains
            surface property. E.g Surfaces, SurfacePoints or Orientations.
        surfaces: If 'all' select all the active data. If a list of surface
            names or a surface name is passed, plot only those.
    """
    if surfaces == 'all':
        geometric_data = data_df
    else:
        geometric_data = pd.concat([data_df.groupby('surface').get_group(group) for group in surfaces])
    return geometric_data


def set_scalar_bar(gempy_vista: GemPyToVista, n_labels: int, surfaces_ids: np.ndarray):
    sargs = gempy_vista.scalar_bar_options
    sargs['title'] = 'id'
    sargs['n_labels'] = n_labels
    sargs['position_y'] = 0.30
    sargs['height'] = -0.25
    sargs['fmt'] = "%.0f"
    gempy_vista.p.add_scalar_bar(**sargs)
    gempy_vista.p.update_scalar_bar_range((surfaces_ids.min(), surfaces_ids.max()))
