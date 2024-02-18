import json
from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel
from datetime import datetime
from .Helpers import MakeIsodataOptionalField


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Station(DataModel):
    md: Optional[float] = field(default=None, metadata=config(field_name="MD"))
    inclination: Optional[float] = None
    azimuth: Optional[float] = None
    elevation: Optional[float] = None
    delta_x: Optional[float] = None
    delta_y: Optional[float] = None
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    time: Optional[datetime] = MakeIsodataOptionalField()


