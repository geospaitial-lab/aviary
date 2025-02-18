from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import (
    TYPE_CHECKING,
    Literal,
    Protocol,
)

import pydantic

# noinspection PyProtectedMember
from aviary._functional.inference.tile_fetcher import (
    composite_fetcher,
    vrt_fetcher,
    wms_fetcher,
)
from aviary.core.enums import (
    InterpolationMode,
    WMSVersion,
)
from aviary.core.type_aliases import (  # noqa: TC001
    BufferSize,
    ChannelTypes,
    ChannelTypeSet,
    Coordinates,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)

if TYPE_CHECKING:
    from aviary.core.tile import Tile


class TileFetcher(Protocol):
    """Protocol for tile fetchers

    Tile fetchers are callables that fetch data from a source given a minimum x and y coordinate.
    These coordinates correspond to the bottom left corner of a tile.
    The tile fetcher is used by the tile set to fetch data for each tile.

    Currently implemented tile fetchers:
        - `CompositeFetcher`: Composes multiple tile fetchers
        - `VRTFetcher`: Fetches a tile from a virtual raster
        - `WMSFetcher`: Fetches a tile from a web map service

    Notes:
        - Implementations must support concurrency (the tile fetcher is called concurrently by the tile loader)
    """

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the source.

        Parameters:
            coordinates: coordinates (x_min, y_min) of the tile

        Returns:
            tile
        """
        ...


class CompositeFetcher:
    """Tile fetcher that composes multiple tile fetchers

    Implements the `TileFetcher` protocol.
    """

    def __init__(
        self,
        tile_fetchers: list[TileFetcher],
        axis: Literal['channel', 'time_step'] = 'channel',
        num_workers: int = 1,
    ) -> None:
        """
        Parameters:
            tile_fetchers: tile fetchers
            axis: axis to concatenate the tiles (`channel`, `time_step`)
            num_workers: number of workers
        """
        self._tile_fetchers = tile_fetchers
        self._axis = axis
        self._num_workers = num_workers

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
        tile_fetchers = []

        for tile_fetcher_config in config.tile_fetchers_configs:
            tile_fetcher_class = globals()[tile_fetcher_config.name]
            tile_fetcher = tile_fetcher_class.from_config(tile_fetcher_config.config)
            tile_fetchers.append(tile_fetcher)

        return cls(
            tile_fetchers=tile_fetchers,
            axis=config.axis,
            num_workers=config.num_workers,
        )

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the sources.

        Parameters:
            coordinates: coordinates (x_min, y_min) of the tile

        Returns:
            tile
        """
        return composite_fetcher(
            coordinates=coordinates,
            tile_fetchers=self._tile_fetchers,
            axis=self._axis,
            num_workers=self._num_workers,
        )


class CompositeFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositeFetcher`

    Attributes:
        tile_fetchers_configs: configurations of the tile fetchers
        axis: axis to concatenate the tiles (`channel`, `time_step`)
        num_workers: number of workers
    """
    tile_fetchers_configs: list[TileFetcherConfig]
    axis: Literal['channel', 'time_step'] = 'channel'
    num_workers: int = 1


class TileFetcherConfig(pydantic.BaseModel):
    """Configuration for tile fetchers

    Attributes:
        name: name of the tile fetcher
        config: configuration of the tile fetcher
    """
    name: str
    config: (
        CompositeFetcherConfig |
        VRTFetcherConfig |
        WMSFetcherConfig
    )


class VRTFetcher:
    """Tile fetcher for virtual rasters

    Implements the `TileFetcher` protocol.
    """
    _FILL_VALUE = 0

    def __init__(
        self,
        path: Path,
        channels: ChannelTypes,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
        buffer_size: BufferSize = 0,
        ignore_channels: ChannelTypeSet | None = None,
    ) -> None:
        """
        Parameters:
            path: path to the virtual raster (.vrt file)
            channels: channels
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            interpolation_mode: interpolation mode (`BILINEAR` or `NEAREST`)
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            ignore_channels: channels to ignore
        """
        self._path = path
        self._channels = channels
        self._tile_size = tile_size
        self._ground_sampling_distance = ground_sampling_distance
        self._interpolation_mode = interpolation_mode
        self._buffer_size = buffer_size
        self._ignore_channels = ignore_channels

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
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the virtual raster.

        Parameters:
            coordinates: coordinates (x_min, y_min) of the tile

        Returns:
            tile
        """
        return vrt_fetcher(
            coordinates=coordinates,
            path=self._path,
            channels=self._channels,
            tile_size=self._tile_size,
            ground_sampling_distance=self._ground_sampling_distance,
            interpolation_mode=self._interpolation_mode,
            buffer_size=self._buffer_size,
            ignore_channels=self._ignore_channels,
            fill_value=self._FILL_VALUE,
        )


class VRTFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VRTFetcher`

    Attributes:
        path: path to the virtual raster (.vrt file)
        channels: channels
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        interpolation_mode: interpolation mode ('bilinear' or 'nearest')
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        ignore_channels: channels to ignore
    """
    path: Path
    channels: ChannelTypes
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR
    buffer_size: BufferSize = 0
    ignore_channels: ChannelTypeSet | None = None


class WMSFetcher:
    """Tile fetcher for web map services

    Implements the `TileFetcher` protocol.
    """
    _FILL_VALUE = '0x000000'

    def __init__(
        self,
        url: str,
        version: WMSVersion,
        layer: str,
        epsg_code: EPSGCode,
        response_format: str,
        channels: ChannelTypes,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        style: str | None = None,
        buffer_size: BufferSize = 0,
        ignore_channels: ChannelTypeSet | None = None,
    ) -> None:
        """
        Parameters:
            url: url of the web map service
            version: version of the web map service (`V1_1_1` or `V1_3_0`)
            layer: name of the layer
            epsg_code: EPSG code
            response_format: format of the response (MIME type, e.g., 'image/png')
            channels: channels
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            style: name of the style
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            ignore_channels: channels to ignore
        """
        self._url = url
        self._version = version
        self._layer = layer
        self._epsg_code = epsg_code
        self._response_format = response_format
        self._tile_size = tile_size
        self._channels = channels
        self._ground_sampling_distance = ground_sampling_distance
        self._style = style
        self._buffer_size = buffer_size
        self._ignore_channels = ignore_channels

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
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the web map service.

        Parameters:
            coordinates: coordinates (x_min, y_min) of the tile

        Returns:
            tile
        """
        return wms_fetcher(
            coordinates=coordinates,
            url=self._url,
            version=self._version,
            layer=self._layer,
            epsg_code=self._epsg_code,
            response_format=self._response_format,
            channels=self._channels,
            tile_size=self._tile_size,
            ground_sampling_distance=self._ground_sampling_distance,
            style=self._style,
            buffer_size=self._buffer_size,
            ignore_channels=self._ignore_channels,
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
        channels: channels
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        style: name of the style
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        ignore_channels: channels to ignore
    """
    url: str
    version: WMSVersion
    layer: str
    epsg_code: EPSGCode
    response_format: str
    channels: ChannelTypes
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    style: str | None = None
    buffer_size: BufferSize = 0
    ignore_channels: ChannelTypeSet | None = None
