from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from .GridCorner import GridCorner
from .Crs import CrsSpec
from ..Geomodels.SimpleGrid import SimpleGrid
from .Coordinate import Coordinate
import math


@dataclass
class GridAxisInfo:
    start: int
    stop: int
    count: int


@dataclass
class GridInfo:
    inline_range: GridAxisInfo
    crossline_range: GridAxisInfo

    @property
    def num_samples(self) -> int:
        return self.inline_range.count * self.crossline_range.count


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GridGeometry:
    corner1: GridCorner
    corner2: GridCorner
    corner3: GridCorner
    corner4: GridCorner
    coordinate_system: CrsSpec
    inclination: Optional[float] = None
    geo_inclination: Optional[float] = None
    inline_bin_interval: Optional[float] = None
    crossline_bin_interval: Optional[float] = None
    area: Optional[float] = None

    @property
    def grid_info(self) -> GridInfo:
        c1 = self.corner1
        c3 = self.corner3
        inline_info = GridAxisInfo(c1.inline, c3.inline, c3.inline - c1.inline + 1)
        crossline_info = GridAxisInfo(c1.crossline, c3.crossline, c3.crossline - c1.crossline + 1)
        return GridInfo(inline_info, crossline_info)

    @classmethod
    def from_simple_grid(cls, grid: SimpleGrid) -> 'GridGeometry':
        """
        Method to set up a simple grid geometry.
        For inclination = 0, rows are west to east, and columns south to north
        Must provide origin, dx, and dy in distance units of provided CRS
        @param grid: a simple grid definition
        @return: a partially filled GridGeometry, where geolocations and geo-inclination not populated.

        NOTES:
        We set up here a CW grid geometry, where rows (inlines) run from East to West, and columns (crosslines)
        run South to North.
        """

        radians = math.radians(grid.inclination)
        x_length = grid.dx * grid.num_cols
        y_length = grid.dy * grid.num_rows
        area = x_length * y_length
        if grid.crs.units.lower() == 'meters':
            area = area / 1000000
        else:
            area = area / 27878400

        c1 = GridCorner(1, 1, grid.origin, None)                    # LL Un-rotated case

        c2_offset = Coordinate(x_length, 0)
        c2_point = c2_offset.rotate(radians) + grid.origin
        c2 = GridCorner(grid.num_cols, 1, c2_point, None)            # LR Un-rotated case

        c3_offset = Coordinate(x_length, y_length)
        c3_point = c3_offset.rotate(radians) + grid.origin
        c3 = GridCorner(grid.num_cols, grid.num_rows, c3_point, None)   # UR Un-rotated case

        c4_offset = Coordinate(0, y_length)
        c4_point = c4_offset.rotate(radians) + grid.origin
        c4 = GridCorner(1, grid.num_rows, c4_point, None)           # UL Un-rotated case

        g = cls(c1, c2, c3, c4, grid.crs, grid.inclination, None, grid.dy, grid.dx, area)
        return g



