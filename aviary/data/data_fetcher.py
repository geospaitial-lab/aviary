from __future__ import annotations

# noinspection PyUnresolvedReferences
from pathlib import Path  # noqa: TCH003
from typing import TYPE_CHECKING, Protocol

import pydantic

if TYPE_CHECKING:
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.data_fetcher import vrt_fetcher

# noinspection PyProtectedMember
from aviary._utils.mixins import FromConfigMixin

# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Coordinate,
    GroundSamplingDistance,
    InterpolationMode,
    TileSize,
)


class DataFetcher(Protocol):
    """Protocol for data fetchers

    Data fetchers are callables that fetch data from a source given a minimum x and y coordinate.
    These coordinates correspond to the bottom left corner of a tile.
    The data fetcher is used by the dataset to fetch data for each tile.

    Currently implemented data fetchers:
        - VRTFetcher: Fetches data from a virtual raster

    Notes:
        - Implementations must support concurrency (the data fetcher is called concurrently by the data loader)
    """

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the source.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        ...


class VRTFetcher(FromConfigMixin):
    """Data fetcher for virtual rasters

    Implements the `DataFetcher` protocol.
    """
    _FILL_VALUE = 0

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
        buffer_size: BufferSize = 0,
        drop_channels: list[int] | None = None,
    ) -> None:
        """
        Parameters:
            path: path to the virtual raster (.vrt file)
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            interpolation_mode: interpolation mode (`BILINEAR` or `NEAREST`)
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            drop_channels: channel indices to drop (supports negative indexing)
        """
        self.path = path
        self.tile_size = tile_size
        self.ground_sampling_distance = ground_sampling_distance
        self.interpolation_mode = interpolation_mode
        self.buffer_size = buffer_size
        self.drop_channels = drop_channels

    @classmethod
    def from_config(
        cls,
        config: VRTFetcherConfig,
    ) -> VRTFetcher:
        """Creates a vrt fetcher from the configuration.

        Parameters:
            config: configuration

        Returns:
            vrt fetcher
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the virtual raster.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        return vrt_fetcher(
            x_min=x_min,
            y_min=y_min,
            path=self.path,
            tile_size=self.tile_size,
            ground_sampling_distance=self.ground_sampling_distance,
            interpolation_mode=self.interpolation_mode,
            buffer_size=self.buffer_size,
            drop_channels=self.drop_channels,
            fill_value=self._FILL_VALUE,
        )


class VRTFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VRTFetcher`

    Attributes:
        path: path to the virtual raster (.vrt file)
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        interpolation_mode: interpolation mode ('bilinear' or 'nearest')
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        drop_channels: channel indices to drop (supports negative indexing)
    """
    path: Path
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR
    buffer_size: BufferSize = 0
    drop_channels: list[int] | None = None
