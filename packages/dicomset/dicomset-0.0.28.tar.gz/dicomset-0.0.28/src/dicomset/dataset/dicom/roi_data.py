from dataclasses import dataclass
import numpy as np
import pydicom as dcm
from typing import Optional

from dicomset import types

@dataclass
class ROIData:
    colour: types.Colour
    data: np.ndarray
    frame_of_reference_uid: str
    name: str
    number: Optional[int] = None
