import numpy as np
from typing import List
from dataclasses import dataclass
from ..Geospatial.Coordinate import Coordinate
from ..Geospatial.Crs import CrsSpec


@dataclass
class SimpleGrid:
    """
    Represents a simple grid.
    Use float('-inf') to represent empty grid values
    """
    name: str
    origin: Coordinate      # x,y coordinate of grid origin
    inclination: float      # rotation of grid clockwise
    dx: float               # grid spacing in x-direction, when not rotated by inclination
    dy: float               # grid spacing in y-direction
    num_rows: int           # number of rows in grid. Rows are laid out along the x-direction  (non-rotated)
    num_cols: int           # number of columns in grid. Columns are laid out along the y-direction (non-rotated)
    crs: CrsSpec            # The projected coordinate system of the x,y origin.
    z_values: List[float]   # Z values of grid, as a 1-D array of 32-bit floats in row major order




