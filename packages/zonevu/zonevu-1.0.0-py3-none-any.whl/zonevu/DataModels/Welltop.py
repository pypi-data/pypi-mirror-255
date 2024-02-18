from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .Survey import Survey
from .DataModel import DataModel


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Welltop(DataModel):
    observation_number: Optional[int] = None
    formation_id: int = -1
    formation_name: str = ''
    formation_symbol: str = ''
    strat_column_id:  int = -1
    md: Optional[float] = field(default=None, metadata=config(field_name="MD"))
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    elevation: Optional[float] = None
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    interpreter: Optional[str] = None
    description: Optional[str] = None
    geoprog_top: bool = False               # Is this a geoprog top?
    survey_id: Optional[int] = None     # Wellbore survey top was picked on
    survey: Optional[Survey] = field(metadata=config(exclude=lambda x: True), default=None) # Do not emit to json
