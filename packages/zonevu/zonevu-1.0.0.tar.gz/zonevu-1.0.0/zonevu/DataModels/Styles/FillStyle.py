from dataclasses import dataclass
from typing import Union, Tuple
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.Styles.Colors import decode_html_color, RgbType


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class FillStyle:
    show: bool = True  # Master switch
    color: str = 'Gray'  # Css color string
    opacity: float = 100  # Opacity of fill color as a percentage [0, 100]

    @staticmethod
    def FromRGBA(r: int, g: int, b: int, a: float) -> 'FillStyle':
        style = FillStyle()
        style.color = 'rgb(%s,%s,%s)' % (r, g, b)
        style.opacity = a
        return style

    def get_color(self, rgb_type: RgbType) -> Union[str, Tuple[float, float, float]]:
        return decode_html_color(self.color, rgb_type)
