from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from .Coordinate import Coordinate
from .GeoLocation import GeoLocation
from typing import Optional


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GridCorner:
    inline: int
    crossline: int
    p: Coordinate
    lat_long: Optional[GeoLocation] = None
