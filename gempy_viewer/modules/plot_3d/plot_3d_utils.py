from typing import Union

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

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


def set_scalar_bar(gempy_vista: GemPyToVista, elements_names: list[str],
                   surfaces_ids: np.ndarray, custom_colors: list = None):
    """
   
    LookupTable (0x7f3d1dc62e00)
      Table Range:                (0.0, 2.0)
      N Values:                   256
      Above Range Color:          None
      Below Range Color:          None
      NAN Color:                  Color(name='darkgray', hex='#a9a9a9ff', opacity=255)
      Log Scale:                  False
      Color Map:                  "viridis"
    """ 
    import pyvista as pv

    # Get mapper actor 
    if gempy_vista.regular_grid_actor is not None:
        mapper_actor = gempy_vista.regular_grid_actor
    elif gempy_vista.surface_points_actor is not None:
        mapper_actor: pv.Actor = gempy_vista.surface_points_actor
    elif gempy_vista.surface_actors is not None:
        mapper_actor: pv.Actor = next(iter(gempy_vista.surface_actors.values()))
    else:
        return None  # * Not a good mapper for the scalar bar

    # Get the lookup table from the mapper
    lut = mapper_actor.mapper.lookup_table

    # Create annotations mapping integers to element names
    annotations = {}
    for e, name in enumerate(elements_names[::-1]):
        # Convert integer to string for the annotation key
        annotations[str(e)] = name

    # Apply annotations to the lookup table
    lut.annotations = annotations

    # Set number of colors to match the number of categories
    n_colors = len(elements_names)
    lut.n_values = n_colors - 1

    # Apply custom colors if provided
    if custom_colors is not None:
        # Check if we have enough colors
        if len(custom_colors) < n_colors:
            raise ValueError(f"Not enough custom colors provided. Got {len(custom_colors)}, need {n_colors}")

        custom_cmap = ListedColormap(custom_colors)
        # Apply the custom colormap to the lookup table
        lut.apply_cmap(cmap=custom_cmap, n_values=n_colors, flip=False)

    else:
        # Apply a default colormap if no custom colors are provided
        lut.apply_cmap(cmap='Set1', n_values=n_colors)

    # Configure scalar bar arguments
    sargs = gempy_vista.scalar_bar_arguments
    min_id, max_id = surfaces_ids.min(), surfaces_ids.max()
    mapper_actor.mapper.scalar_range = (min_id - .5, max_id + .5)

    sargs["mapper"] = mapper_actor.mapper
    sargs["n_labels"] = 0

    # Add scalar bar
    gempy_vista.p.add_scalar_bar(**sargs)

    # Update scalar bar range to match surface IDs range
