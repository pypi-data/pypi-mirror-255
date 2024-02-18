from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase, config


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Conditioning:
    """
    Represents a ZoneVu geosteering curve conditioning parameter set
    """
    # Amplitude Range filter
    AmplClip: bool = False
    AmplClipRangeMin: Optional[float] = None
    AmplClipRangeMax: Optional[float] = None
    AmplClipInclusiveNotExclusive: Optional[bool] = None

    # MD Range filter
    MDClip: bool = False
    MDClipRangeMin: Optional[float] = None
    MDClipRangeMax: Optional[float] = None
    MDClipInclusiveNotExclusive: Optional[bool] = None

    # Despiking filter.
    Despike: bool = False
    VarianceThreshold: Optional[
        float] = None  # Absolute variance that is acceptable as a number in the units of the curve data.
    DespikeLen: Optional[int] = None  # Should be an odd number. Number of pts in despiking filter.

    # Interpolation filter.
    Interpolate: bool = False
    MaxGap: Optional[int] = None

    # SmoothingFilter filter.
    Smooth: bool = False
    SmoothingLen: Optional[int] = None  # Number of points in smoothing filter.

    # Amplitude normalization filter.
    Normalize: bool = False
    Bias: Optional[float] = None  # Amplitude shift
    Scalar: Optional[float] = None  # Amplitude multiplier

