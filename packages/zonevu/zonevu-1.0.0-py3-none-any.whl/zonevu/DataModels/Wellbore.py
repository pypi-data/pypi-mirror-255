from typing import Optional, Union, List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from strenum import StrEnum
from .DataModel import DataModel
from .Welllog import Welllog
from .Survey import Survey, DeviationSurveyUsageEnum
from .Welltop import Welltop
from .Geosteering.Interpretation import Interpretation
from .Curve import Curve, AppMnemonicCodeEnum
from .Note import Note


class WellBoreShapeEnum(StrEnum):
    BuildAndHold = 'BuildAndHold'
    Deviated = 'Deviated'
    DoubleKickoff = 'DoubleKickoff'
    Horizontal = 'Horizontal'
    S_Shaped = 'S_Shaped'
    Vertical = 'Vertical'
    Unknown = 'Unknown'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Wellbore(DataModel):
    # Represents a ZoneVu Wellbore object
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    shape: Optional[WellBoreShapeEnum] = WellBoreShapeEnum.Unknown
    welllogs: list[Welllog] = field(default_factory=list[Welllog])
    surveys: list[Survey] = field(default_factory=list[Survey])
    tops: list[Welltop] = field(default_factory=list[Welltop])
    interpretations: list[Interpretation] = field(default_factory=list[Interpretation])
    notes: list[Note] = field(default_factory=list[Note])

    def copy_ids_from(self, source: 'Wellbore'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.welllogs, source.welllogs)
        DataModel.merge_lists(self.surveys, source.surveys)
        DataModel.merge_lists(self.tops, source.tops)
        DataModel.merge_lists(self.interpretations, source.interpretations)

    def make_trimmed_copy(self) -> 'Wellbore':
        # Make a copy that is suitable for creating wells through the Web API
        # In this case, don't include any lists of sub well data. Those get created via Web API separately
        copy = Wellbore()
        copy.name = self.name
        copy.id = self.id
        copy.row_version = self.row_version
        copy.uwi = self.uwi
        copy.shape = self.shape
        return copy

    @property
    def actual_survey(self) -> Union[Survey, None]:
        surveys = self.surveys
        survey = next((s for s in surveys if s.usage == DeviationSurveyUsageEnum.Actual), None)  # Get actual survey
        return survey

    @property
    def plan_surveys(self) -> List[Survey]:
        surveys = self.surveys
        plans = [s for s in surveys if s.usage == DeviationSurveyUsageEnum.Plan]
        return plans

    def get_first_curve(self, code: AppMnemonicCodeEnum) -> Union[Curve, None]:
        for log in self.welllogs:
            for curve in log.curves:
                if curve.system_mnemonic == code:
                    return curve
        return None
