from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase
from ..DataModel import DataModel
from .Pick import Pick
from .CurveDef import CurveDef
from .Horizon import Horizon, TypewellHorizonDepth


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Interpretation(DataModel):
    description: Optional[str] = ''
    starred: bool = False
    target_wellbore_id: int = -1
    target_wellbore_name: Optional[str] = None
    target_wellbore_number: Optional[str] = None
    target_formation_id: int = -1
    target_formation_name: Optional[str] = None
    target_formation_member_name: Optional[str] = None
    owner_name: Optional[str] = None
    owner_id: int = -1
    thickness: Optional[float] = None
    coordinate_system: Optional[str] = None
    picks: list[Pick] = field(default_factory=list[Pick])
    curve_defs: list[CurveDef] = field(default_factory=list[CurveDef])
    horizons: list[Horizon] = field(default_factory=list[Horizon])
    typewell_horizon_depths: Optional[list[TypewellHorizonDepth]] = field(default_factory=list[TypewellHorizonDepth])

    def copy_ids_from(self, source: 'Interpretation'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.picks, source.picks)
        DataModel.merge_lists(self.curve_defs, source.curve_defs)
        DataModel.merge_lists(self.horizons, source.horizons)

