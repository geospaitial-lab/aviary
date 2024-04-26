from enum import Enum

import numpy as np
import numpy.typing as npt
import rasterio as rio

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

    def to_rio(self):
        """
        | Converts the interpolation mode to the rasterio resampling mode.

        :return: rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


class GeospatialFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class SetFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
