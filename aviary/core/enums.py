from enum import Enum as BaseEnum

import rasterio as rio


class Enum(BaseEnum):

    def __str__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
        """
        return self.value


class Channel(Enum):
    """
    Attributes:
        B: blue channel
        G: green channel
        NIR: near-infrared channel
        R: red channel
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
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    """
    Attributes:
        BILINEAR: bilinear mode
        NEAREST: nearest mode
    """
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


class WMSVersion(Enum):
    """
    Attributes:
        V1_1_1: version 1.1.1
        V1_3_0: version 1.3.0
    """
    V1_1_1 = '1.1.1'
    V1_3_0 = '1.3.0'
