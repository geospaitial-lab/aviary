from __future__ import annotations

from pathlib import Path  # noqa: TCH003
from typing import TYPE_CHECKING, Protocol

import pydantic

if TYPE_CHECKING:
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.data_fetcher import (
    composite_fetcher,
    vrt_fetcher,
    wms_fetcher,
)

# noinspection PyProtectedMember
from aviary._utils.mixins import FromConfigMixin

# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Coordinate,
    EPSGCode,
    GroundSamplingDistance,
    InterpolationMode,
    TileSize,
    WMSVersion,
)


class DataFetcher(Protocol):
    """Protocol for data fetchers

    Data fetchers are callables that fetch data from a source given a minimum x and y coordinate.
    These coordinates correspond to the bottom left corner of a tile.
    The data fetcher is used by the dataset to fetch data for each tile.

    Currently implemented data fetchers:
        - CompositeFetcher: Composes multiple data fetchers
        - VRTFetcher: Fetches data from a virtual raster
        - WMSFetcher: Fetches data from a web map service

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


class CompositeFetcher(FromConfigMixin):
    """Data fetcher that composes multiple data fetchers

    Implements the `DataFetcher` protocol.
    """

    def __init__(
        self,
        data_fetchers: list[DataFetcher],
        num_workers: int = 1,
    ) -> None:
        """
        Parameters:
            data_fetchers: data fetchers
            num_workers: number of workers
        """
        self.data_fetchers = data_fetchers
        self.num_workers = num_workers

    @classmethod
    def from_config(
        cls,
        config: CompositeFetcherConfig,
    ) -> CompositeFetcher:
        """Creates a composite fetcher from the configuration.

        Parameters:
            config: configuration

        Returns:
            composite fetcher
        """
        data_fetchers = []

        for data_fetcher_config in config.data_fetchers_configs:
            data_fetcher_class = globals()[data_fetcher_config.name]
            data_fetcher = data_fetcher_class.from_config(data_fetcher_config.config)
            data_fetchers.append(data_fetcher)

        return cls(
            data_fetchers=data_fetchers,
            num_workers=config.num_workers,
        )

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the sources.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        return composite_fetcher(
            x_min=x_min,
            y_min=y_min,
            data_fetchers=self.data_fetchers,
            num_workers=self.num_workers,
        )


class CompositeFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositeFetcher`

    Attributes:
        data_fetchers_configs: configurations of the data fetchers
        num_workers: number of workers
    """
    data_fetchers_configs: list[DataFetcherConfig]
    num_workers: int = 1


class DataFetcherConfig(pydantic.BaseModel):
    """Configuration for data fetchers

    Attributes:
        name: name of the data fetcher
        config: configuration of the data fetcher
    """
    name: str
    config: VRTFetcherConfig | WMSFetcherConfig


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


class WMSFetcher(FromConfigMixin):
    """Data fetcher for web map services

    Implements the `DataFetcher` protocol.
    """
    _FILL_VALUE = '0x000000'

    def __init__(
        self,
        url: str,
        version: WMSVersion,
        layer: str,
        epsg_code: EPSGCode,
        response_format: str,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        style: str | None = None,
        buffer_size: BufferSize = 0,
        drop_channels: list[int] | None = None,
    ) -> None:
        """
        Parameters:
            url: url of the web map service
            version: version of the web map service (`V1_1_1` or `V1_3_0`)
            layer: name of the layer
            epsg_code: EPSG code
            response_format: format of the response (MIME type, e.g., 'image/png')
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            style: name of the style
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            drop_channels: channel indices to drop (supports negative indexing)
        """
        self.url = url
        self.version = version
        self.layer = layer
        self.epsg_code = epsg_code
        self.response_format = response_format
        self.tile_size = tile_size
        self.ground_sampling_distance = ground_sampling_distance
        self.style = style
        self.buffer_size = buffer_size
        self.drop_channels = drop_channels

    @classmethod
    def from_config(
        cls,
        config: WMSFetcherConfig,
    ) -> WMSFetcher:
        """Creates a wms fetcher from the configuration.

        Parameters:
            config: configuration

        Returns:
            wms fetcher
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

    def __call__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
    ) -> npt.NDArray:
        """Fetches data from the web map service.

        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate

        Returns:
            data
        """
        return wms_fetcher(
            x_min=x_min,
            y_min=y_min,
            url=self.url,
            version=self.version,
            layer=self.layer,
            epsg_code=self.epsg_code,
            response_format=self.response_format,
            tile_size=self.tile_size,
            ground_sampling_distance=self.ground_sampling_distance,
            style=self.style,
            buffer_size=self.buffer_size,
            drop_channels=self.drop_channels,
            fill_value=self._FILL_VALUE,
        )


class WMSFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `WMSFetcher`

    Attributes:
        url: url of the web map service
        version: version of the web map service ('1.1.1' or '1.3.0')
        layer: name of the layer
        epsg_code: EPSG code
        response_format: format of the response (MIME type, e.g., 'image/png')
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        style: name of the style
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        drop_channels: channel indices to drop (supports negative indexing)
    """
    url: str
    version: WMSVersion
    layer: str
    epsg_code: EPSGCode
    response_format: str
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    style: str | None = None
    buffer_size: BufferSize = 0
    drop_channels: list[int] | None = None
