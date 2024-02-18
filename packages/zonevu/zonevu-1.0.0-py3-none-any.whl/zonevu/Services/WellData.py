from typing import TypedDict, Optional, Set
from strenum import StrEnum


class WellData(StrEnum):
    default = 'default'     # Default behavior is to not load anything except well headers and wellbores
    logs = 'logs'
    curves = 'curves'       # Refers to well log curve sample data, not the curve object (i.e. - the headers)
    surveys = 'surveys'
    tops = 'tops'
    fracs = 'fracs'
    geosteering = 'geosteering'
    notes = 'notes'
    all = 'all'             # If specified, load all well data, as long as 'default' flag not present


class WellDataOptions:
    well_data: Set[WellData]

    def __init__(self, well_data: Set[WellData]):
        self.well_data = well_data

    def _calc_option(self, well_data: WellData) -> bool:
        return (well_data in self.well_data or self.all) and self.some

    @property
    def all(self):
        return WellData.all in self.well_data

    @property
    def some(self) -> bool:
        return WellData.default not in self.well_data

    @property
    def welllogs(self) -> bool:
        return self._calc_option(WellData.logs)

    @property
    def surveys(self) -> bool:
        return self._calc_option(WellData.surveys)

    @property
    def curves(self) -> bool:
        return self._calc_option(WellData.curves)

    @property
    def tops(self) -> bool:
        return self._calc_option(WellData.tops)

    @property
    def geosteering(self) -> bool:
        return self._calc_option(WellData.geosteering)

    @property
    def notes(self) -> bool:
        return self._calc_option(WellData.notes)
