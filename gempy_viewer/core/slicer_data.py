from dataclasses import dataclass

import numpy as np


@dataclass(init=True)
class SlicerData:
    x: str
    y: str
    Gx: str
    Gy: str
    select_projected_p: np.ndarray
    select_projected_o: np.ndarray


