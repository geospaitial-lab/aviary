from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class DataFetcherInfo:
    bounding_box: BoundingBox
    dtype: DType
    epsg_code: EPSGCode
    ground_sampling_distance: GroundSamplingDistance
    num_channels: int


class DType(Enum):
    BOOL = np.bool_
    FLOAT32 = np.float32
    UINT8 = np.uint8

    @classmethod
    def from_rio(
        cls,
        dtype: str,
    ) -> 'DType':
        """
        | Converts the rasterio data type to the data type.

        :param dtype: rasterio data type
        :return: data type
        """
        mapping = {
            rio.dtypes.bool_: DType.BOOL,
            rio.dtypes.float32: DType.FLOAT32,
            rio.dtypes.uint8: DType.UINT8,
        }
        return mapping[dtype]


class GeospatialFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


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


class SetFilterMode(Enum):
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
