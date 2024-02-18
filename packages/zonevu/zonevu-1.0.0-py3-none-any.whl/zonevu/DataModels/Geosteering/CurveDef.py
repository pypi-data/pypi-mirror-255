from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase, config
from ..DataModel import DataModel
from .Conditioning import Conditioning
from strenum import StrEnum


class CurveGroupRoleEnum(StrEnum):
    Image = 'Image'
    Litho = 'Litho'
    Splice = 'Splice'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CurveDef(DataModel):
    """
    Represents a ZoneVu geosteering curve definition
    """
    curve_id: Optional[int] = None
    curve_group_id: Optional[int] = None
    role: Optional[CurveGroupRoleEnum] = None
    active: bool = False
    conditioning: Optional[Conditioning] = None

