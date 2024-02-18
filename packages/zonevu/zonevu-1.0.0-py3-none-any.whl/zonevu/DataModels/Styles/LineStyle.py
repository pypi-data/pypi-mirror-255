from dataclasses import dataclass
from typing import Union, Tuple
from dataclasses_json import dataclass_json, LetterCase
from zonevu.zonevu.DataModels.Styles.Colors import decode_html_color, RgbType


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class LineStyle:
    show: bool = True  # Master switch
    color: str = 'gray'  # Css color string
    thickness: float = 1  # Thickness of the line
    dashed: bool = False  # Whether the line is dashed

    @staticmethod
    def FromRGB(r: int, g: int, b: int) -> 'LineStyle':
        style = LineStyle()
        style.color = 'rgb(%s,%s,%s)' % (r, g, b)
        return style

    def get_color(self, rgb_type: RgbType) -> Union[str, Tuple[float, float, float]]:
        return decode_html_color(self.color, rgb_type)