from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from ..DataModel import DataModel
from strenum import StrEnum
from ..Geospatial.GeoLocation import GeoLocation
from ..Geospatial.GeoBox import GeoBox
from json import dumps, loads
import pygeojson as geo
import math


class LayerTypeEnum(StrEnum):
    Unspecified = "Unspecified"
    Lease = "Lease"
    Hardline = "Hardline"
    Pad = "Pad"


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class UserLayer(DataModel):
    project_id: int = -1
    description: Optional[str] = None
    layer_type: LayerTypeEnum = LayerTypeEnum.Unspecified
    geo_json: Optional[str] = None
    extents: Optional[GeoBox] = None

    @property
    def geojson(self) -> geo.FeatureCollection:
        fc = geo.loads(self.geo_json)
        if fc.bbox is None:
            upper_right = self.extents.upper_right
            lower_left = self.extents.lower_left
            minx = min(upper_right.longitude, lower_left.longitude)
            maxx = max(upper_right.longitude, lower_left.longitude)
            miny = min(upper_right.latitude, lower_left.latitude)
            maxy = max(upper_right.latitude, lower_left.latitude)
            bbox = (minx, miny, maxx, maxy)
            features2 = geo.FeatureCollection(fc.features, bbox, fc.type, fc.extra_attributes)
            return features2
        else:
            return fc
