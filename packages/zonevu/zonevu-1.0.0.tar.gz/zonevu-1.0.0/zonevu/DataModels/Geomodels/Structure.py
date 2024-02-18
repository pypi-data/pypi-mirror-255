from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.DataModel import DataModel
from zonevu.zonevu.DataModels.Geospatial.GridGeometry import GridGeometry
import numpy as np


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Structure(DataModel):
    formation_id: int = 0
    formation_name: str = ''
    geometry: GridGeometry = None
    description: Optional[str] = None
    z_values: Optional[np.ndarray] = None  # numpy float array
