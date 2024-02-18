from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase, config
from ..DataModel import DataModel


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Pick(DataModel):
    # Represents a ZoneVu geosteering interpretation pick
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    md: float = field(default=0, metadata=config(field_name="MD"))
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    target_tvt: Optional[float] = field(default=None, metadata=config(field_name="TargetTVT"))
    target_tvd: Optional[float] = field(default=None, metadata=config(field_name="TargetTVD"))
    target_elevation: Optional[float] = field(default=None, metadata=config(field_name="TargetElevation"))
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    dx: Optional[float] = field(default=None, metadata=config(field_name="DX"))
    dy: Optional[float] = field(default=None, metadata=config(field_name="DY"))
    elevation: Optional[float] = None
    block_flag: bool = False
    fault_flag: bool = False
    type_wellbore_id: int = -1
    type_curve_def_id: Optional[int] = None
