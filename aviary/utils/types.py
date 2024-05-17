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
    """
    Attributes:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
        dtype: data type of each channel
        epsg_code: EPSG code
        ground_sampling_distance: ground sampling distance in meters
        num_channels: number of channels
    """
    bounding_box: BoundingBox
    dtype: list[DType]
    epsg_code: EPSGCode
    ground_sampling_distance: GroundSamplingDistance
    num_channels: int


class DType(Enum):
    """
    Attributes:
        BOOL: boolean data type
        FLOAT32: 32-bit floating point data type
        UINT8: 8-bit unsigned integer data type
    """
    BOOL = np.bool_
    FLOAT32 = np.float32
    UINT8 = np.uint8

    @classmethod
    def from_rio(
        cls,
        dtype: str,
    ) -> 'DType':
        """Converts the rasterio data type to the data type.

        Parameters:
            dtype: rasterio data type

        Returns:
            data type
        """
        mapping = {
            rio.dtypes.bool_: DType.BOOL,
            rio.dtypes.float32: DType.FLOAT32,
            rio.dtypes.uint8: DType.UINT8,
        }
        return mapping[dtype]


class GeospatialFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'

    def to_rio(self) -> rio.enums.Resampling:
        """Converts the interpolation mode to the rasterio resampling mode.

        Returns:
            rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


class SetFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
        UNION: union mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
