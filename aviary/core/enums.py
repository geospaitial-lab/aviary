#  Copyright (C) 2024-2026 Marius Maryniak
#  Copyright (C) 2026 Alexander Roß
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from enum import Enum as BaseEnum
from typing import (
    TYPE_CHECKING,
    overload,
)

import numpy as np
import rasterio as rio

if TYPE_CHECKING:
    from aviary.core.type_aliases import ChannelNameSet


class Enum(BaseEnum):  # noqa: D101

    def __str__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        return self.value


class ChannelName(Enum):
    """
    Attributes:
        ASPECT: Aspect channel
        B: Blue channel
        DEM: Digital elevation model channel
        G: Green channel
        HILLSHADE: Hillshade channel
        NIR: Near-infrared channel
        R: Red channel
        SLOPE: Slope channel
    """
    ASPECT = 'aspect'
    B = 'b'
    DEM = 'dem'
    G = 'g'
    HILLSHADE = 'hillshade'
    NIR = 'nir'
    R = 'r'
    SLOPE = 'slope'


_built_in_channel_names = frozenset(channel_name.value for channel_name in ChannelName)


@overload
def _coerce_channel_name(
    channel_name: ChannelName,
) -> ChannelName:
    ...


@overload
def _coerce_channel_name(
    channel_name: str,
) -> ChannelName | str:
    ...


@overload
def _coerce_channel_name(
    channel_name: None,
) -> None:
    ...


def _coerce_channel_name(
    channel_name: ChannelName | str | None,
) -> ChannelName | str | None:
    """Coerces `channel_name` to `ChannelName`.

    Parameters:
        channel_name: Channel name

    Returns:
        Channel name
    """
    if channel_name is None:
        return None

    if isinstance(channel_name, str) and channel_name in _built_in_channel_names:
        return ChannelName(channel_name)

    return channel_name


def _coerce_channel_names(
    channel_names:
        ChannelName | str |
        ChannelNameSet |
        bool |
        None,
) -> ChannelNameSet | bool:
    """Coerces `channel_names` to `ChannelNameSet`.

    Parameters:
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True)

    Returns:
        Channel names or all channels (True)
    """
    if channel_names is True:
        return True

    if channel_names is False or channel_names is None:
        return set()

    if isinstance(channel_names, (ChannelName | str)):
        return {_coerce_channel_name(channel_name=channel_names)}

    return {
        _coerce_channel_name(channel_name=channel_name)
        for channel_name in channel_names
    }


def _coerce_layer_names(
    layer_names: str | set[str] | bool | None,
) -> set[str] | bool:
    """Coerces `layer_names` to `set[str]`.

    Parameters:
        layer_names: Layer name, layer names, no layers (False or None), or all layers (True)

    Returns:
        Layer names or all layers (True)
    """
    if layer_names is True:
        return True

    if layer_names is False or layer_names is None:
        return set()

    if isinstance(layer_names, str):
        return {layer_names}

    return layer_names


class Connectivity(Enum):
    """
    Attributes:
        FOUR: 4-connectivity
        EIGHT: 8-connectivity
    """
    FOUR = 4
    EIGHT = 8


class DType(Enum):
    """
    Attributes:
        Bool: Boolean type
        FLOAT16: Half-precision floating-point type
        FLOAT32: Single-precision floating-point type
        FLOAT64: Double-precision floating-point type
        INT8: 8-bit signed integer type
        INT16: 16-bit signed integer type
        INT32: 32-bit signed integer type
        UINT8: 8-bit unsigned integer type
        UINT16: 16-bit unsigned integer type
        UINT32: 32-bit unsigned integer type
    """
    Bool = 'bool'
    FLOAT16 = 'float16'
    FLOAT32 = 'float32'
    FLOAT64 = 'float64'
    INT8 = 'int8'
    INT16 = 'int16'
    INT32 = 'int32'
    UINT8 = 'uint8'
    UINT16 = 'uint16'
    UINT32 = 'uint32'

    def to_numpy(self) -> np.dtype:
        """Converts the data type to the numpy data type.

        Returns:
            Numpy data type
        """
        mapping = {
            DType.Bool: np.bool_,
            DType.FLOAT16: np.float16,
            DType.FLOAT32: np.float32,
            DType.FLOAT64: np.float64,
            DType.INT8: np.int8,
            DType.INT16: np.int16,
            DType.INT32: np.int32,
            DType.UINT8: np.uint8,
            DType.UINT16: np.uint16,
            DType.UINT32: np.uint32,
        }
        return mapping[self]


_supported_dtypes = frozenset(dtype.value for dtype in DType)


class GeospatialFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: Difference mode
        INTERSECTION: Intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    """
    Attributes:
        BILINEAR: Bilinear mode
        NEAREST: Nearest mode
    """
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'

    def to_rio(self) -> rio.enums.Resampling:
        """Converts the interpolation mode to the rasterio resampling mode.

        Returns:
            Rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


class LogLevel(Enum):
    """
    Attributes:
        TRACE: Trace level
        DEBUG: Debug level
        INFO: Info level
        SUCCESS: Success level
        WARNING: Warning level
        ERROR: Error level
        CRITICAL: Critical level
    """
    TRACE = 'trace'
    DEBUG = 'debug'
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class OSMType(Enum):
    """
    Attributes:
        NODE: node type
        WAY: way type
        RELATION: relation type
    """
    NODE = 'node'
    WAY = 'way'
    RELATION = 'relation'


class SetFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: Difference mode
        INTERSECTION: Intersection mode
        UNION: Union mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'


class SlopeUnit(Enum):
    """
    Attributes:
        DEGREES: Degrees
        PERCENT: Percent
    """
    DEGREES = 'degrees'
    PERCENT = 'percent'


class WMSVersion(Enum):
    """
    Attributes:
        V1_1_1: Version 1.1.1
        V1_3_0: Version 1.3.0
    """
    V1_1_1 = '1.1.1'
    V1_3_0 = '1.3.0'
