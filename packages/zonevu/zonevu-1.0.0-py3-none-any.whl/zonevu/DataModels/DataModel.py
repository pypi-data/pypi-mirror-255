from typing import Optional, Type
from dataclasses import dataclass, field, fields
from dataclasses_json import dataclass_json, LetterCase
from strenum import StrEnum


class ChangeAgentEnum(StrEnum):
    Unknown = 'Unknown'
    GuiCreate = 'GuiCreate'
    GuiImport = 'GuiImport'
    GuiBulkImport = 'GuiBulkImport'
    WebApi = 'WebApi'


class WellElevationUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class DataModel:
    id: int = -1            # Mandatory
    name: Optional[str] = None
    row_version: Optional[str] = None

    def merge_from(self, source: 'DataModel'):
        self.__dict__.update(source.__dict__)

    def copy_ids_from(self, source: 'DataModel'):
        self.id = source.id

    @staticmethod
    def merge_lists(dst_list: list['DataModel'], src_list: list['DataModel']):
        for (dst, src) in zip(dst_list, src_list):
            if dst is not None and src is not None:
                dst.copy_ids_from(src)

