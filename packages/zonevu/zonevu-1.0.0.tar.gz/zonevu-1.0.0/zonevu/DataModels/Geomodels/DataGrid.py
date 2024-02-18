from typing import Optional
from enum import StrEnum
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.DataModel import DataModel
from zonevu.zonevu.DataModels.Geospatial.GridGeometry import GridGeometry
import numpy as np


class GridUsageEnum(StrEnum):
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class DataGrid(DataModel):
    geometry: GridGeometry = None
    description: Optional[str] = None
    usage: GridUsageEnum = GridUsageEnum.Undefined
    average_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    z_values: Optional[np.ndarray] = None  # numpy 32-bit (single precision float array). Must be 32-bit floats!

