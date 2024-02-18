from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel
from strenum import StrEnum, PascalCaseStrEnum


class GeoPeriodEnum(StrEnum):
    Quaternary = 'Quaternary',
    Neogene = 'Neogene',
    Paleogene = 'Paleogene',
    Cretaceous = 'Cretaceous',
    Jurassic = 'Jurassic',
    Triassic = 'Triassic',
    Permian = 'Permian',
    Carboniferous = 'Carboniferous',
    Devonian = 'Devonian',
    Silurian = 'Silurian',
    Ordovician = 'Ordovician',
    Cambrian = 'Cambrian',
    Precambrian = 'Precambrian'


class LithologyTypeEnum(PascalCaseStrEnum):
    Unset = 'Unset',
    Sandstone = 'Sandstone',
    Shale = 'Shale',
    Limestone = 'Limestone',
    Dolomite = 'Dolomite',
    Chalk = 'Chalk',
    Marl = 'Marl',
    MudstoneRich = 'MudstoneRich',
    MudstoneLean = 'MudstoneLean',
    Bentonite = 'Bentonite',
    Coal = 'Coal',
    Chert = 'Chert',
    Anhydrite = 'Anhydrite',
    Siltstone = 'Siltstone',
    ShalySand = 'ShalySand'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Formation(DataModel):
    formation_name: Optional[str] = None
    member_name: Optional[str] = None
    strat_col_order: int = -1
    symbol: str = ''
    color: Optional[str] = None
    description: Optional[str] = None
    period: Optional[GeoPeriodEnum] = None
    lithology_type: Optional[LithologyTypeEnum] = None

    def __post_init__(self):
        self.name = self.formation_name
