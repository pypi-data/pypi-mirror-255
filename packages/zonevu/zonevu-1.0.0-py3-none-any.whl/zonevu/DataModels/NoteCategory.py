from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from .DataModel import DataModel


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class NoteCategory(DataModel):
    description: Optional[str] = None
