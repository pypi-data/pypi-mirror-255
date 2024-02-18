from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
import math
from typing import Tuple


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GeoLocation:
    latitude: float
    longitude: float

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.longitude, self.latitude

    @staticmethod
    def error(l1: 'GeoLocation', l2: 'GeoLocation') -> float:
        loc_err_lat = l1.latitude - l2.latitude
        loc_err_lon = l1.longitude - l2.longitude
        e = math.sqrt(math.pow(loc_err_lat, 2) + math.pow(loc_err_lon, 2))
        return e

    def arc_latitude(self) -> float:
        return self.latitude * math.pi / 180

    def arc_longitude(self) -> float:
        return self.longitude * math.pi / 180

    @staticmethod
    def bearing(s: 'GeoLocation', f: 'GeoLocation') -> float:
        latitude1 = s.arc_latitude()
        latitude2 = f.arc_latitude()
        longitudeDifference = f.arc_longitude() - s.arc_longitude()
        y = math.sin(longitudeDifference) * math.cos(latitude2)
        x = math.cos(latitude1) * math.sin(latitude2) - \
            math.sin(latitude1) * math.cos(latitude2) * math.cos(longitudeDifference)
        bearing = (math.atan2(y, x) * 180 / math.pi + 360) % 360
        return bearing

    @classmethod
    def lower_left_of(cls, l1: 'GeoLocation', l2: 'GeoLocation') -> 'GeoLocation':
        min_latitude = min(l1.latitude, l2.latitude)
        min_longitude = min(l1.longitude, l2.longitude)
        return cls(min_latitude, min_longitude)

    @classmethod
    def upper_right_of(cls, l1: 'GeoLocation', l2: 'GeoLocation') -> 'GeoLocation':
        max_latitude = max(l1.latitude, l2.latitude)
        max_longitude = max(l1.longitude, l2.longitude)
        return cls(max_latitude, max_longitude)

