import numpy as np

from gempy import GeoModel
from gempy.core.grid_modules.grid_types import Sections
from gempy_viewer.modules.plot_2d.visualization_2d import Plot2D


def plot_section_traces(gempy_model: GeoModel, ax, section_names: list[str] = None):
    sections: Sections = gempy_model.grid.sections
    
    if section_names is None:
        section_names = list(sections.names)

    for section_name in section_names:
        if section_name not in sections.df.index:
            continue
            
        x1, y1 = np.asarray(sections.df.loc[section_name, 'start'])
        x2, y2 = np.asarray(sections.df.loc[section_name, 'stop'])
        ax.plot([x1, x2], [y1, y2], label=section_name, linestyle='--')
        ax.legend(frameon=True)
