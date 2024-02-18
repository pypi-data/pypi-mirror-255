# import json
# from dataclasses import dataclass
# from ..Zonevu import Zonevu
# from ..DataModels.WellEntry import WellEntry
# from ..DataModels.Wellbore import Wellbore
# from ..DataModels.Well import Well
# # from dacite import from_dict
#
#
# @dataclass
# class WellEntryService:
#     _zonevu: Zonevu = None
#
#     def __init__(self, zv: Zonevu):
#         self._zonevu = zv
#
#     def get_wells(self, matchToken=None) -> list[Well]:
#         wellsUrl = "wells"
#         if matchToken is not None:
#             wellsUrl += "/%s" % matchToken
#         r = self._zonevu.CallAPI(wellsUrl)
#         wellList = json.loads(r.text)
#         entries = [Well.from_dict(w) for w in wellList]
#         return entries
