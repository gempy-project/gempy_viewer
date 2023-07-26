from typing import Union

import pandas as pd


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
