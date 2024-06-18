from pathlib import Path
from typing import Protocol

import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.data_fetcher import (
    vrt_data_fetcher,
    vrt_data_fetcher_info,
)

# noinspection PyProtectedMember
from aviary._utils.types import (
    BoundingBox,
    BufferSize,
    Coordinate,
    DType,
    EPSGCode,
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
        - VRTDataFetcher: Fetches data from a virtual raster
        - WMSDataFetcher: Fetches data from a web map service

    Notes:
        - Implementations must support concurrency (the data fetcher may be called concurrently by the dataloader)
    """

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the source given a minimum x and y coordinate.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        ...


class VRTDataFetcher:
    """Data fetcher for virtual rasters

    Implements the DataFetcher protocol.
    """
    _FILL_VALUE = 0

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
        buffer_size: BufferSize = None,
        drop_channels: list[int] = None,
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

        self._data_fetcher_info = vrt_data_fetcher_info(
            path=self.path,
        )

    @property
    def src_bounding_box(self) -> BoundingBox:
        """Bounding box of the virtual raster

        Returns:
            bounding box
        """
        return self._data_fetcher_info.bounding_box

    @property
    def src_dtype(self) -> list[DType]:
        """Data type of each channel of the virtual raster

        Returns:
            data type of each channel
        """
        return self._data_fetcher_info.dtype

    @property
    def src_epsg_code(self) -> EPSGCode:
        """EPSG code of the virtual raster

        Returns:
            EPSG code
        """
        return self._data_fetcher_info.epsg_code

    @property
    def src_ground_sampling_distance(self) -> GroundSamplingDistance:
        """Ground sampling distance of the virtual raster

        Returns:
            ground sampling distance in meters
        """
        return self._data_fetcher_info.ground_sampling_distance

    @property
    def src_num_channels(self) -> int:
        """Number of channels of the virtual raster

        Returns:
            number of channels
        """
        return self._data_fetcher_info.num_channels

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the virtual raster given a minimum x and y coordinate.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        return vrt_data_fetcher(
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
