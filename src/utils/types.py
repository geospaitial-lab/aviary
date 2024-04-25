from enum import Enum

import numpy as np
import numpy.typing as npt

BoundingBox = tuple[int, int, int, int]
BufferSize = int
Coordinates = npt.NDArray[np.int32]
EPSGCode = int
GroundSamplingDistance = float
TileSize = int
XMax = int
XMin = int
YMax = int
YMin = int


class InterpolationMode(Enum):
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'


class GeospatialFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class SetFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
