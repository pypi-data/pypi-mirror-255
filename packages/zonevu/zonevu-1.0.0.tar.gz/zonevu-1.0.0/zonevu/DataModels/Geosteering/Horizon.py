from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase, config
from ..DataModel import DataModel
from zonevu.zonevu.DataModels.Styles.LineStyle import LineStyle
from zonevu.zonevu.DataModels.Styles.FillStyle import FillStyle
from strenum import StrEnum


class GeosteerHorizonRole(StrEnum):
    Default = 'Default'
    ZoneTop = 'ZoneTop'
    ZoneBottom = 'ZoneBottom'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Horizon(DataModel):
    """
    Represents a ZoneVu geosteering curve definition
    """
    role: GeosteerHorizonRole = GeosteerHorizonRole.Default
    formation_id: int = -1
    show: bool = True
    line_style: Optional[LineStyle] = None
    fill_style: Optional[FillStyle] = None
    zone_name: Optional[str] = None
    defines_zone: Optional[bool] = None


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class TypewellHorizonDepth(DataModel):
    """
    Represents a depth of a geosteering horizon on a type well, which often is a well top depth.
    Includes tvt, which is relative to the type_wellbore_target top tvd.
    """
    type_wellbore_id: int = 0
    horizon_id: int = 0
    md: float = field(default=0.0, metadata=config(field_name="MD"))
    tvd: float = field(default=0.0, metadata=config(field_name="TVD"))
    tvt: float = field(default=0.0, metadata=config(field_name="TVT"))

    @property
    def key(self) -> str:
        return TypewellHorizonDepth.make_key(self.type_wellbore_id, self.horizon_id)

    @staticmethod
    def make_key(type_wellbore_id: int, horizon_id: int) -> str:
        return '%s-%s' % (type_wellbore_id, horizon_id)
