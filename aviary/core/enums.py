from enum import Enum as BaseEnum
from typing import overload

import rasterio as rio

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
        B: Blue channel
        G: Green channel
        NIR: Near-infrared channel
        R: Red channel
    """
    B = 'b'
    G = 'g'
    NIR = 'nir'
    R = 'r'


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


class WMSVersion(Enum):
    """
    Attributes:
        V1_1_1: Version 1.1.1
        V1_3_0: Version 1.3.0
    """
    V1_1_1 = '1.1.1'
    V1_3_0 = '1.3.0'
