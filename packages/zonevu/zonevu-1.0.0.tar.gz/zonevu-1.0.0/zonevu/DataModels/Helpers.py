from datetime import datetime
from strenum import StrEnum, PascalCaseStrEnum
from typing import TypedDict, Optional, Union
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from marshmallow import fields


def iso_to_datetime(value: Union[str, None]) -> Union[datetime, None]:
    if value is None:
        return None
    try:
        date = datetime.fromisoformat(value)
        return date
    except TypeError:
        return None
    except ValueError:
        return None


def date_time_to_iso(value: Union[datetime, None]) -> Union[str, None]:
    if value is None:
        return None
    return value.isoformat()


isodateFieldConfig = config(
    encoder=date_time_to_iso,
    decoder=iso_to_datetime,
    mm_field=fields.DateTime(format='iso')
)
isodateFieldConfigHide = {
    "encoder": lambda dt: dt.isoformat(),
    "decoder": lambda dt_str: datetime.fromisoformat(dt_str),
}
isodateOptional = field(default=None, metadata=isodateFieldConfig)


def MakeIsodataOptionalField():
    return field(default=None, metadata=isodateFieldConfig)


class DepthUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'



