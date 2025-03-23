from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable

import pydantic

# noinspection PyProtectedMember
from aviary._functional.tile.tile_fetcher import (
    composite_fetcher,
    vrt_fetcher,
    wms_fetcher,
)
from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    WMSVersion,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    ChannelKey,
    Coordinates,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)

if TYPE_CHECKING:
    from aviary.core.tiles import Tile


class TileFetcher(Protocol):
    """Protocol for tile fetchers

    Tile fetchers are callables that fetch a tile from a source given a minimum x and y coordinate.
    These coordinates correspond to the bottom left corner of a tile.

    Implemented tile fetchers:
        - `CompositeFetcher`: Composes multiple tile fetchers
        - `VRTFetcher`: Fetches a tile from a virtual raster
        - `WMSFetcher`: Fetches a tile from a web map service
    """

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the source.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            Tile
        """
        ...


class TileFetcherConfig(pydantic.BaseModel):
    """Configuration for tile fetchers

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        name: 'MyTileFetcher'
        config:
          ...
        ```

    Attributes:
        name: Name
        config: Configuration
    """
    name: str
    config: (
        CompositeFetcherConfig |
        VRTFetcherConfig |
        WMSFetcherConfig |
        pydantic.BaseModel
    )


_registry: dict[str, tuple[type[TileFetcher], type[pydantic.BaseModel]]] = {}


class TileFetcherFactory:
    """Factory for tile fetchers"""

    @staticmethod
    def create(
        config: TileFetcherConfig,
    ) -> TileFetcher:
        """Creates a tile fetcher from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tile fetcher
        """
        try:
            tile_fetcher_class = globals()[config.name]
            return tile_fetcher_class.from_config(config=config.config)
        except KeyError:
            registry_entry = _registry.get(config.name)

            if registry_entry is None:
                message = (
                    'Invalid config! '
                    f'The tile fetcher {config.name} is not registered.'
                )
                raise AviaryUserError(message) from None

            tile_fetcher_class, _ = registry_entry
            # noinspection PyUnresolvedReferences
            return tile_fetcher_class.from_config(config=config.config)

    @staticmethod
    def register(
        tile_fetcher_class: type[TileFetcher],
        config_class: type[pydantic.BaseModel],
    ) -> None:
        """Registers a tile fetcher.

        Parameters:
            tile_fetcher_class: Tile fetcher class
            config_class: Configuration class
        """
        _registry[tile_fetcher_class.__name__] = (tile_fetcher_class, config_class)


def register_tile_fetcher(config_class: type[pydantic.BaseModel]) -> Callable:
    """Registers a tile fetcher.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator
    """
    def decorator(cls: type[TileFetcher]) -> type[TileFetcher]:
        TileFetcherFactory.register(
            tile_fetcher_class=cls,
            config_class=config_class,
        )
        return cls
    return decorator


class CompositeFetcher:
    """Tile fetcher that composes multiple tile fetchers

    Notes:
        - The tile fetchers are called concurrently depending on the maximum number of threads
        - If the maximum number of threads is 1, the tile fetchers are composed vertically, i.e., in sequence
        - If the maximum number of threads is greater than 1, the tile fetchers are composed horizontally, i.e.,
            in parallel

    Implements the `TileFetcher` protocol.
    """

    def __init__(
        self,
        tile_fetchers: list[TileFetcher],
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            tile_fetchers: Tile fetchers
            max_num_threads: Maximum number of threads
        """
        self._tile_fetchers = tile_fetchers
        self._max_num_threads = max_num_threads if len(self._tile_fetchers) > 1 else 1

    @classmethod
    def from_config(
        cls,
        config: CompositeFetcherConfig,
    ) -> CompositeFetcher:
        """Creates a composite fetcher from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Composite fetcher
        """
        tile_fetchers = [
            TileFetcherFactory.create(config=tile_fetcher_config)
            for tile_fetcher_config in config.tile_fetcher_configs
        ]
        return cls(
            tile_fetchers=tile_fetchers,
            max_num_threads=config.max_num_threads,
        )

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the sources.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            Tile
        """
        return composite_fetcher(
            coordinates=coordinates,
            tile_fetchers=self._tile_fetchers,
            max_num_threads=self._max_num_threads,
        )


class CompositeFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositeFetcher`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        tile_fetcher_configs:
          - ...
          ...
        max_num_threads: null
        ```

    Attributes:
        tile_fetcher_configs: Configurations of the tile fetchers
        max_num_threads: Maximum number of threads -
            defaults to None
    """
    tile_fetcher_configs: list[TileFetcherConfig]
    max_num_threads: int | None = None


class VRTFetcher:
    """Tile fetcher for virtual rasters

    Implements the `TileFetcher` protocol.
    """
    _FILL_VALUE = 0

    def __init__(
        self,
        path: Path,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            list[ChannelName | str | ChannelKey | None] |
            None,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
        buffer_size: BufferSize = 0,
    ) -> None:
        """
        Parameters:
            path: Path to the virtual raster (.vrt file)
            channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations (if None, the channel is ignored)
            tile_size: Tile size in meters
            ground_sampling_distance: Ground sampling distance in meters
            interpolation_mode: Interpolation mode (`BILINEAR` or `NEAREST`)
            buffer_size: Buffer size in meters
        """
        self._path = path
        self._channel_keys = channel_keys
        self._tile_size = tile_size
        self._ground_sampling_distance = ground_sampling_distance
        self._interpolation_mode = interpolation_mode
        self._buffer_size = buffer_size

    @classmethod
    def from_config(
        cls,
        config: VRTFetcherConfig,
    ) -> VRTFetcher:
        """Creates a VRT fetcher from the configuration.

        Parameters:
            config: Configuration

        Returns:
            VRT fetcher
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the virtual raster.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            Tile
        """
        return vrt_fetcher(
            coordinates=coordinates,
            path=self._path,
            channel_keys=self._channel_keys,
            tile_size=self._tile_size,
            ground_sampling_distance=self._ground_sampling_distance,
            interpolation_mode=self._interpolation_mode,
            buffer_size=self._buffer_size,
            fill_value=self._FILL_VALUE,
        )


class VRTFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VRTFetcher`

    Create the configuration from a config file:
        - Use 'bilinear' or 'nearest' instead of `InterpolationMode.BILINEAR` or `InterpolationMode.NEAREST`
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        path: 'path/to/my_vrt.vrt'
        channel_keys:
          - 'r'
          - 'g'
          - 'b'
        tile_size: 128
        ground_sampling_distance: .2
        interpolation_mode: 'bilinear'
        buffer_size: 0
        ```

    Attributes:
        path: Path to the virtual raster (.vrt file)
        channel_keys: Channel name, channel name and time step combination, channel names,
            or channel name and time step combinations (if None, the channel is ignored)
        tile_size: Tile size in meters
        ground_sampling_distance: Ground sampling distance in meters
        interpolation_mode: Interpolation mode (`BILINEAR` or `NEAREST`) -
            defaults to `BILINEAR`
        buffer_size: Buffer size in meters (specifies the area around the tile that is additionally fetched) -
            defaults to 0
    """
    path: Path
    channel_keys: (
        ChannelName | str |
        ChannelKey |
        list[ChannelName | str | ChannelKey | None] |
        None
    )
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR
    buffer_size: BufferSize = 0


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
        channel_keys:
            ChannelName | str |
            ChannelKey |
            list[ChannelName | str | ChannelKey | None] |
            None,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        style: str | None = None,
        buffer_size: BufferSize = 0,
    ) -> None:
        """
        Parameters:
            url: URL of the web map service
            version: Version of the web map service (`V1_1_1` or `V1_3_0`)
            layer: Layer
            epsg_code: EPSG code
            response_format: Format of the response (MIME type, e.g., 'image/png')
            channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations (if None, the channel is ignored)
            tile_size: Tile size in meters
            ground_sampling_distance: Ground sampling distance in meters
            style: Style
            buffer_size: Buffer size in meters
        """
        self._url = url
        self._version = version
        self._layer = layer
        self._epsg_code = epsg_code
        self._response_format = response_format
        self._channel_keys = channel_keys
        self._tile_size = tile_size
        self._ground_sampling_distance = ground_sampling_distance
        self._style = style
        self._buffer_size = buffer_size

    @classmethod
    def from_config(
        cls,
        config: WMSFetcherConfig,
    ) -> WMSFetcher:
        """Creates a WMS fetcher from the configuration.

        Parameters:
            config: Configuration

        Returns:
            WMS fetcher
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Tile:
        """Fetches a tile from the web map service.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            Tile
        """
        return wms_fetcher(
            coordinates=coordinates,
            url=self._url,
            version=self._version,
            layer=self._layer,
            epsg_code=self._epsg_code,
            response_format=self._response_format,
            channel_keys=self._channel_keys,
            tile_size=self._tile_size,
            ground_sampling_distance=self._ground_sampling_distance,
            style=self._style,
            buffer_size=self._buffer_size,
            fill_value=self._FILL_VALUE,
        )


class WMSFetcherConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `WMSFetcher`

    Create the configuration from a config file:
        - Use '1.1.1' or '1.3.0' instead of `WMSVersion.V1_1_1` or `WMSVersion.V1_3_0`
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        url: 'https://www.my-wms.com'
        version: '1.3.0'
        layer: 'my_layer'
        epsg_code: 25832
        response_format: 'image/png'
        channel_keys:
          - 'r'
          - 'g'
          - 'b'
        tile_size: 128
        ground_sampling_distance: .2
        style: null
        buffer_size: 0
        ```

    Attributes:
        url: URL of the web map service
        version: Version of the web map service (`V1_1_1` or `V1_3_0`)
        layer: Layer
        epsg_code: EPSG code
        response_format: Format of the response (MIME type, e.g., 'image/png')
        channel_keys: Channel name, channel name and time step combination, channel names,
            or channel name and time step combinations (if None, the channel is ignored)
        tile_size: Tile size in meters
        ground_sampling_distance: Ground sampling distance in meters
        style: Style -
            defaults to None
        buffer_size: Buffer size in meters -
            defaults to 0
    """
    url: str
    version: WMSVersion
    layer: str
    epsg_code: EPSGCode
    response_format: str
    channel_keys: (
        ChannelName | str |
        ChannelKey |
        list[ChannelName | str | ChannelKey | None] |
        None
    )
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    style: str | None = None
    buffer_size: BufferSize = 0
