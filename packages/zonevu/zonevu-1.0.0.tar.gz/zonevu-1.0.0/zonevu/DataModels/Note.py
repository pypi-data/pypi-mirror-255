from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel
from datetime import datetime
from .Helpers import MakeIsodataOptionalField


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Note(DataModel):
    md: float = field(default=None, metadata=config(field_name="MD"))
    owner: str = ''
    creation_time: datetime = MakeIsodataOptionalField()
    wellbore_id: int = -1
    description: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[int] = None
    interpretation: Optional[str] = None
    interpretation_id: Optional[int] = None
