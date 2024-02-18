import json
from typing import Optional, Union
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from .DataModel import DataModel
from strenum import StrEnum
from .Station import Station


class DeviationSurveyUsageEnum(StrEnum):
    Plan = 'Plan'
    Actual = 'Actual'


class AzimuthReferenceEnum(StrEnum):
    Unknown = 'Unknown'
    TrueNorth = 'TrueNorth'
    MagneticNorth = 'MagneticNorth'
    GridNorth = 'GridNorth'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Survey(DataModel):
    description: Optional[str] = None
    azimuth_reference: Optional[AzimuthReferenceEnum] = AzimuthReferenceEnum.Unknown
    azimuth_offset: Optional[float] = 0
    usage: Optional[DeviationSurveyUsageEnum] = DeviationSurveyUsageEnum.Actual
    stations: list[Station] = field(default_factory=list[Station])

    def copy_ids_from(self, source: 'Survey'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.stations, source.stations)

    def find_md(self, tvd: float) -> Union[float, None]:
        # Search for the MD corresponding to the provided TVD in the monotonic portion of the wellbore
        try:
            stations = self.stations
            if len(stations) == 0:
                return None
            station_first = stations[0]
            station_last = stations[-1]
            if tvd < station_first.tvd or tvd > station_last.tvd:
                return None
            if tvd == station_last.tvd:
                return station_last.md
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]

                if s2.tvd <= s1.tvd:
                    return None     # We have reached the non-monotonic portion of the well bore so give up.

                if s1.tvd <= tvd < s2.tvd:
                    dtvd = s2.tvd - s1.tvd
                    dmd = s2.md - s1.md
                    md = s1.md + dmd * (tvd - s1.tvd) / dtvd
                    return md
            return None
        except Exception as err:
            return None

        # return tvd

    def find_tvd(self, md: float) -> Union[float, None]:
        try:
            stations = self.stations
            if len(stations) == 0:
                return None
            station_first = stations[0]
            station_last = stations[-1]
            if md < station_first.md or md > station_last.md:
                return None
            if md == station_last.md:
                return station_last.tvd
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]
                if s1.md <= md < s2.md:
                    dmd = s2.md - s1.md
                    dtvd = s2.tvd - s1.tvd
                    tvd = s1.tvd + dtvd * (md - s1.md) / dmd
                    return tvd
            return None
        except Exception as err:
            return None
