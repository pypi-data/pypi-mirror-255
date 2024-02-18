import dataclasses
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from .Wellbore import Wellbore
from dataclasses_json import dataclass_json, LetterCase, config
from strenum import StrEnum, PascalCaseStrEnum
from enum import auto
import copy
import re
from .Helpers import MakeIsodataOptionalField
from .DataModel import DataModel, ChangeAgentEnum, WellElevationUnitsEnum


class WellElevationTypeEnum(StrEnum):
    KB = 'KB'
    Wellhead = 'Wellhead'
    Ground = 'Ground'
    Water = 'Water'


class WellDirectionEnum(StrEnum):
    Unknown = 'Unknown'
    HuffNPuff = 'HuffNPuff'
    Injector = 'Injector'
    Producer = 'Producer'
    Uncertain = 'Uncertain'


class WellPurposeEnum(StrEnum):
    Unknown = 'Unknown'
    Appraisal = 'Appraisal'
    Appraisal_Confirmation = 'Appraisal_Confirmation'
    Appraisal_Exploratory = 'Appraisal_Exploratory'
    Exploration = 'Exploration'
    Exploration_DeeperPoolWildcat = 'Exploration_DeeperPoolWildcat'
    Exploration_NewFieldWildcat = 'Exploration_NewFieldWildcat'
    Exploration_NewPoolWildcat = 'Exploration_NewPoolWildcat'
    Exploration_OutpostWildcat = 'Exploration_OutpostWildcat'
    Exploration_ShallowerPoolWildcat = 'Exploration_ShallowerPoolWildcat'
    Development = 'Development'
    Development_InfillDevelopment = 'Development_InfillDevelopment'
    Development_Injector = 'Development_Injector'
    Development_Producer = 'Development_Producer'
    FluidStorage = 'FluidStorage'
    FluidStorage_Gas = 'FluidStorage_Gas'
    GeneralServices = 'GeneralServices'
    GeneralServices_BoreholeReacquisition = 'GeneralServices_BoreholeReacquisition'
    GeneralServices_Observation = 'GeneralServices_Observation'
    GeneralServices_Relief = 'GeneralServices_Relief'
    GeneralServices_Research = 'GeneralServices_Research'
    GeneralServices_Research_DrillTest = 'GeneralServices_Research_DrillTest'
    GeneralServices_Research_StratTest = 'GeneralServices_Research_StratTest'
    Mineral = 'Mineral'


class WellFluidEnum(StrEnum):
    Unknown = 'Unknown'
    Air = 'Air'
    Condensate = 'Condensate'
    Dry = 'Dry'
    Gas = 'Gas'
    Gas_Water = 'Gas_Water'
    Non_Hydrocarbon_Gas = 'Non_Hydrocarbon_Gas'
    Non_Hydrocarbon_Gas_CO2 = 'Non_Hydrocarbon_Gas_CO2'
    Oil = 'Oil'
    Oil_Gas = 'Oil_Gas'
    Oil_Water = 'Oil_Water'
    Steam = 'Steam'
    Water = 'Water'
    Water_Brine = 'Water_Brine'
    Water_FreshWater = 'Water_FreshWater'


class EnvironmentTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Land = 'Land'
    Marine = 'Marine'
    Transition = 'Transition'


class WellStatusEnum(PascalCaseStrEnum):
    Unknown = auto()
    Active = auto()
    ActiveInjecting = auto()
    ActiveProducing = auto()
    Completed = auto()
    Drilling = auto()
    PartiallyPlugged = auto()
    Permitted = auto()
    PluggedAndAbandoned = auto()
    Proposed = auto()
    Sold = auto()
    Suspended = auto()
    TemporarilyAbandoned = auto()
    Testing = auto()
    Tight = auto()
    WorkingOver = auto()


@dataclass_json(letter_case=LetterCase.PASCAL, undefined=None)
@dataclass
class Well(DataModel):
    """
    Represents a ZoneVu Well Object
    """
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodataOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodataOptionalField()
    operator: Optional[str] = None
    number: Optional[str] = None
    description: Optional[str] = None
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    original_uwi: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    status: Optional[WellStatusEnum] = WellStatusEnum.Unknown
    environment: Optional[EnvironmentTypeEnum] = EnvironmentTypeEnum.Unknown
    purpose: Optional[WellPurposeEnum] = WellPurposeEnum.Unknown
    fluid_type: Optional[WellFluidEnum] = WellFluidEnum.Unknown
    well_direction: Optional[WellDirectionEnum] = WellDirectionEnum.Unknown
    property_number: Optional[str] = None
    afe_number: Optional[str] = field(default=None, metadata=config(field_name="AFENumber"))
    spud_date: Optional[datetime] = MakeIsodataOptionalField()
    completion_date: Optional[datetime] = MakeIsodataOptionalField()
    target_zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    field: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    elevation: Optional[float] = None
    elevation_type: Optional[WellElevationTypeEnum] = WellElevationTypeEnum.KB
    elevation_units: Optional[WellElevationUnitsEnum] = None
    target_zone_id: Optional[int] = None
    location_datum: Optional[str] = None
    strat_column_id: Optional[int] = None
    azimuth: Optional[float] = None
    wellbores: Optional[list[Wellbore]] = dataclasses.field(default_factory=list[Wellbore])

    def init_primary_wellbore(self):
        primary_wellbore = Wellbore()
        primary_wellbore.name = 'Primary'
        self.wellbores = []
        self.wellbores.append(primary_wellbore)

    def copy_ids_from(self, source: 'Well'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.wellbores, source.wellbores)

    @property
    def full_name(self) -> str:
        if self.number is None:
            return self.name
        else:
            return '%s %s' % (self.name, self.number)

    @property
    def primary_wellbore(self) -> Wellbore:
        """
        Gets the primary wellbore on the well. Normally, there is only a wellbore per well,
        and it is the primary wellbore
        """
        return self.wellbores[0]

    def make_trimmed_copy(self) -> 'Well':
        # Make a copy that is suitable for creating wells through the Web API
        wellbores = self.wellbores
        self.wellbores = []
        well_copy = copy.deepcopy(self)
        well_copy.wellbores = [bore.make_trimmed_copy() for bore in wellbores]
        self.wellbores = wellbores
        return well_copy

    @staticmethod
    def fix_uwi(uwi: str) -> str:
        return uwi
        # pattern = r"^[\d-]+$"
        # # Use re.match to check if the string matches the pattern
        # digits_and_dashes = bool(re.match(pattern, uwi))
        #
        # if digits_and_dashes:
        #     digits_only = uwi.replace("-", "")
        #     N = len(digits_only)
        #     if N < 16:
        #         digits_only += "0" * (16 - N)
        #     return digits_only
        # else:
        #     return uwi
