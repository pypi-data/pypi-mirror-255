from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.DataModel import DataModel, WellElevationUnitsEnum
from .Curve import Curve, AppMnemonicCodeEnum
from strenum import StrEnum


class WellLogTypeEnum(StrEnum):
    Digital = 'Digital'
    Raster = 'Raster'
    Witsml = 'Witsml'
    Frac = 'Frac'


class WellLogIndexTypeEnum(StrEnum):
    Depth = 'Depth'
    Time = 'Time'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Welllog(DataModel):
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[WellLogTypeEnum] = None
    start_depth: Optional[float] = None
    end_depth: Optional[float] = None
    step_length: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    step_time: Optional[float] = None
    depth_units: Optional[WellElevationUnitsEnum] = None
    index_type: Optional[WellLogIndexTypeEnum] = None
    curves: list[Curve] = field(default_factory=list[Curve])
    index_curve_id: Optional[int] = None
    # las_file: Optional[str] = None  # ASCII text of LAS file

    def copy_ids_from(self, source: 'Welllog'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.curves, source.curves)

    def find_curve(self, mne: AppMnemonicCodeEnum) -> Curve:
        curve = next((c for c in self.curves if c.system_mnemonic == mne), None)
        return curve



