from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.DataModel import DataModel, ChangeAgentEnum
from zonevu.zonevu.DataModels.Geomodels.DataGrid import DataGrid
from zonevu.zonevu.DataModels.Geomodels.Structure import Structure
from datetime import datetime
from zonevu.zonevu.DataModels.Helpers import MakeIsodataOptionalField


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Geomodel(DataModel):
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodataOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodataOptionalField()
    division_id: int = 0
    division: str = ''
    strat_column_id: int = 0
    strat_column_name: str = ''
    description: Optional[str] = None
    data_grids: list[DataGrid] = field(default_factory=list[DataGrid])
    structures: list[Structure] = field(default_factory=list[Structure])

