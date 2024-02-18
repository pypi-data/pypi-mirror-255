import json
from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from .DataModel import DataModel
import numpy as np
from strenum import StrEnum


class AppMnemonicCodeEnum(StrEnum):
    NotSet = "NotSet"
    DEPT = "DEPT"  # "Hole depth (MD)"
    GR = "GR"  # "Gamma ray"
    ROP = "ROP"  # "Rate of penetration"
    WOB = "WOB"  # "Weight on bit"
    INCL = "INCL"  # "Inclination"
    AZIM = "AZIM"  # "Azimuth"
    GAS = "GAS"  # "Total Gas"
    BIT = "BIT"  # "Bit depth"
    GRDEPT = "GRDEPT"  # "Gamma ray depth"
    DENS = "DENS"  # "Density"
    RESS = "RESS"  # "Shallow Resistivity"
    RESM = "RESM"  # "Medium Resistivity"
    RESD = "RESD"  # "Deep Resistivity"
    DTC = "DTC"  # "Compressional Sonic Travel Time"
    DTS = "DTS"  # "Shear Sonic Travel Time"
    SP = "SP"  # "Spontaneous Potential"
    PHIN = "PHIN"  # "Neutron Porosity"
    PHID = "PHID"  # "Density Porosity"
    NMR = "NMR"  # "Nuclear Magnetic Resonance"
    PE = "PE"  # "Photoelectric cross section"
    AGR = "AGR"  # "Azimuthal Gamma Ray"
    PHIE = "PHIE"  # "Porosity"
    SW = "SW"  # "Water Saturation"
    VSHL = "VSHL"  # "Shale Content"
    HCP = "HCP"  # "HydocarbonPorosity"
    TIME = "TIME"  # "Time (UTC)"

    @classmethod
    def _missing_(cls, value):
        return AppMnemonicCodeEnum.NotSet


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Curve(DataModel):
    description: Optional[str] = None
    mnemonic: str = ''
    system_mnemonic: AppMnemonicCodeEnum = field(default_factory=lambda: AppMnemonicCodeEnum.NotSet)
    unit: Optional[str] = None
    samples: Optional[np.ndarray] = None    # numpy float array
    registered: bool = True

    @classmethod
    def from_dict(cls, dict_obj):
        instance = cls(**dict_obj)
        return instance


