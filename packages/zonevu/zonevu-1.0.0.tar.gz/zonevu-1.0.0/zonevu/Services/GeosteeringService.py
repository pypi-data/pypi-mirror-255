import json
from typing import Union
from zonevu.zonevu.DataModels import Interpretation
from zonevu.zonevu.DataModels import Wellbore
from .Client import Client
from enum import Enum


class PickAdjustEnum(Enum):
    BlockBoundaries = 0
    NormalFaults = 1
    MidPoints = 2


class GeosteeringService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_interpretations(self, wellbore_id: int) -> list[Interpretation]:
        interpsUrl = "geosteer/interpretations/%s" % wellbore_id
        items = self.client.get(interpsUrl)
        interps = [Interpretation.from_dict(w) for w in items]
        return interps

    def load_interpretations(self, wellbore: Wellbore) -> list[Interpretation]:
        interps = self.get_interpretations(wellbore.id)
        wellbore.interpretations = interps
        return interps

    def get_interpretation(self, interp_id, pic_adjust: PickAdjustEnum = PickAdjustEnum.BlockBoundaries,
                           interval: Union[float, None] = None, normalize: Union[bool, None] = None) -> Interpretation:
        interpUrl = "geosteer/interpretation/%s" % interp_id

        query_params = {'pickadjust': pic_adjust.value}
        if interval is not None:
            query_params['interval'] = str(interval)
        if normalize is not None:
            query_params['normalize'] = str(normalize)

        r = self.client.call_api_get(interpUrl, query_params)
        interp_dict = json.loads(r.text)
        interp = Interpretation.from_json(r.text)
        return interp

    def load_interpretation(self, interp: Interpretation, pic_adjust: PickAdjustEnum = PickAdjustEnum.BlockBoundaries,
                            interval: Union[float, None] = None, normalize: Union[bool, None] = None) -> Interpretation:
        full_interp = self.get_interpretation(interp.id, pic_adjust, interval, normalize)
        # interp.copy_ids_from(full_interp)
        for field in full_interp.__dataclass_fields__:
            setattr(interp, field, getattr(full_interp, field))
        return interp

    def add_interpretation(self, wellbore_id: int, interp: Interpretation, overwrite: bool = False) -> None:
        url = "geosteer/interpretation/add/%s" % wellbore_id
        query_params = {'overwrite': overwrite, 'rowversion': ''}
        item = self.client.post(url, interp.to_dict(), True, query_params)
        server_interp: Interpretation = Interpretation.from_dict(item)
        interp.copy_ids_from(server_interp)

    def delete_interpretation(self, interp: Interpretation) -> None:
        url = "geosteer/interpretation/delete/%s" % interp.id
        query_params = {} if interp.row_version is None else {'rowversion': interp.row_version}
        self.client.delete(url, query_params)


