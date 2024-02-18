from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class WellEntry:
    # Represents a ZoneVu Well catalog entry Object (lightweight)
    id: int = -1
    uwi: Optional[str] = None
    name: str = ''
    number: Optional[str] = None
    description: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    status: Optional[str] = None

    def fullName(self):
        name = '%s %s' % (self.Name, self.Number)
        return name
    FullName = property(fullName)


