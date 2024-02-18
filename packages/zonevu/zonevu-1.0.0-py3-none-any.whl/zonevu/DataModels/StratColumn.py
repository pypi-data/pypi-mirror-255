from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel
from .Formation import Formation


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class StratColumn(DataModel):
    description: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    basin: Optional[str] = None
    formations: list[Formation] = field(default_factory=list[Formation])

    def copy_ids_from(self, source: 'StratColumn'):
        super().copy_ids_from(source)
        DataModel.merge_lists(self.formations, source.formations)
