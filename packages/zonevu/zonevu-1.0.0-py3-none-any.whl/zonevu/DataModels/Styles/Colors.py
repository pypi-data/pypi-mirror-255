"""
Color related utilities
"""

from typing import Union, Tuple
from enum import StrEnum


class RgbType(StrEnum):
    Rgb1 = 'Rgb1'
    Rgb255 = 'Rgb255'


def decode_html_color(color: str, rgb_type: RgbType) -> Union[str, Tuple[float, float, float]]:
    """
    Convert HTML color string to a typical python style color. Html rgb values are in range [0, 255]
    @param rgb_type: range of rgb values
    @param color: and html color string that is either a well known HTML color string or a html rgb string
    @return: a python compatible color
    """
    if color.startswith('rgb'):
        r: int
        g: int
        b: int
        r, g, b = map(int, color[color.index('(') + 1:color.index(')')].split(','))
        divisor = 1 if rgb_type == RgbType.Rgb255 else 255
        output = (r / divisor, g / divisor, b / divisor)
        return output
    else:
        return color

