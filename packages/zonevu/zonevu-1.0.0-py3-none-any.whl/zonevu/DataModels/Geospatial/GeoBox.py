from typing import List, Tuple
from functools import reduce
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from .GeoLocation import GeoLocation
from zonevu.zonevu.Services.Error import ZonevuError


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GeoBox:
    """
    Represents the bounds of a map in geolocations
    """
    lower_left: GeoLocation
    upper_right: GeoLocation

    @classmethod
    def from_locations(cls, locations: List[GeoLocation]):
        if len(locations) == 0:
            raise ZonevuError.local('cannot create a GeoBox from a zero length list of geolocations')

        lower_left = reduce(lambda l1, l2: GeoLocation.lower_left_of(l1, l2), locations)
        upper_right = reduce(lambda l1, l2: GeoLocation.upper_right_of(l1, l2), locations)
        g = cls(upper_right, lower_left)
        return g

    @classmethod
    def from_boxes(cls, b1: 'GeoBox', b2: 'GeoBox') -> 'GeoBox':
        lower_left = GeoLocation.lower_left_of(b1.lower_left, b2.lower_left)
        upper_right = GeoLocation.upper_right_of(b1.upper_right, b2.upper_right)
        return cls(lower_left, upper_right)

    @classmethod
    def from_box_list(cls, boxes: List['GeoBox']) -> 'GeoBox':
        largest_box = reduce(lambda b1, b2: GeoBox.from_boxes(b1, b2), boxes)
        return largest_box

    @property
    def tuple(self) -> Tuple[float, float, float, float]:
        geobox_tuple = self.lower_left.tuple + self.upper_right.tuple
        return geobox_tuple


