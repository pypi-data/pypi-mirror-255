from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel, ChangeAgentEnum
from strenum import PascalCaseStrEnum
from enum import auto
from datetime import datetime
from .Helpers import MakeIsodataOptionalField
from .WellEntry import WellEntry
from zonevu.zonevu.DataModels.Geospatial.Crs import DistanceUnitsEnum


class ProjectTypeEnum(PascalCaseStrEnum):
    Unspecified = auto()
    Prospect = auto()
    AreaOfInterest = auto()
    Development = auto()
    Operations = auto()
    Job = auto()
    Subscription = auto()
    DealRoom = auto()
    DataRoom = auto()
    SeismicSurvey = auto()
    Well = auto()
    Pad = auto()


# class DistanceUnitsEnum(StrEnum):
#     Undefined = 'Undefined'
#     Meters = 'Meters'
#     Feet = 'Feet'
#     FeetUS = 'FeetUS'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class ProjectEntry(DataModel):
    division_id: int = 0
    division: str = ''
    number: Optional[str] = None
    description: Optional[str] = None
    # project_type: ProjectTypeEnum = ProjectTypeEnum.Unspecified


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Project(DataModel):
    division_id: int = 0
    division: str = ''
    crs_projection: str = ''
    crs_zone: str = ''
    crs_distance_units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined
    # epsg_code: Optional[int] = field(default=None, metadata=config(field_name="EPSGCode"))
    number: Optional[str] = None
    description: Optional[str] = None
    project_type: ProjectTypeEnum = ProjectTypeEnum.Unspecified
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodataOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodataOptionalField()
    property_number: Optional[str] = None
    afe_number: Optional[str] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    producing_field: Optional[str]  = field(default=None, metadata=config(field_name="Field"))
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    is_active: bool = False
    is_complete: bool = False
    is_confidential: bool = False
    start_date: Optional[datetime] = MakeIsodataOptionalField()
    completion_date: Optional[datetime] = MakeIsodataOptionalField()
    confidential_release_date: Optional[datetime] = MakeIsodataOptionalField()
    wells: list[WellEntry] = field(default_factory=list[WellEntry])
