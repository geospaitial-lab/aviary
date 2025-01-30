from enum import Enum as BaseEnum

import rasterio as rio


class Enum(BaseEnum):  # noqa: D101

    def __str__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        return self.value


class Channel(Enum):
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


class Device(Enum):
    """
    Attributes:
        CPU: CPU device
        CUDA: CUDA device
    """
    CPU = 'cpu'
    CUDA = 'cuda'


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
