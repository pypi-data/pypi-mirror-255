from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Company:
    Version: str = ''  # API Version
    RuntimeVersion: str = '?'  # ZoneVu server runtime version
    CompanyName: str = ''
    Notice: str = ''

    def printNotice(self):
        print("Zonevu Web API Version %s. Zonevu Server Version %s." % (self.Version, self.RuntimeVersion))
        print(self.Notice)
        print("ZoneVu account '%s'" % self.CompanyName)
        print()

