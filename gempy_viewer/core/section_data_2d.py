﻿from dataclasses import dataclass
from enum import auto, Enum

from matplotlib.axes import Axes

from gempy_viewer.core.slicer_data import SlicerData


class SectionType(Enum):
    SECTION: int = auto()
    ORTHOGONAL: int = auto()
    TOPOGRAPHY: int = auto()
    
    
@dataclass
class SectionData2D:
    section_type: SectionType
    slicer_data: SlicerData
    ax: Axes