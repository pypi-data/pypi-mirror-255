from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Coordinate:
    x: float = 0
    y: float = 0

    # def rotate(self, angle: float) -> 'Coordinate':
    #     """
    #     Rotates this point around the origin by an angle
    #     @param angle: angle from x-axis in radians
    #     @return: the rotated point
    #     """
    #     x = self.x * math.cos(angle) - self.y * math.sin(angle)
    #     y = self.x * math.sin(angle) + self.y * math.cos(angle)
    #     return Coordinate(x, y)
    #
    # def __add__(self, other: 'Coordinate') -> 'Coordinate':
    #     return Coordinate(self.x + other.x, self.y + other.y)
