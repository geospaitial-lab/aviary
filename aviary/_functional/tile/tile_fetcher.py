from __future__ import annotations

import warnings
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.windows
import requests

from aviary.core.bounding_box import BoundingBox

# noinspection PyProtectedMember
from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    WMSVersion,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.tiles import Tile

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelKey,
        Coordinates,
        EPSGCode,
        GroundSamplingDistance,
        TileSize,
    )
    from aviary.tile.tile_fetcher import TileFetcher


def composite_fetcher(
    coordinates: Coordinates,
    tile_fetchers: list[TileFetcher],
    max_num_threads: int | None = None,
) -> Tile:
    """Fetches a tile from the sources.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of the tile in meters
        tile_fetchers: Tile fetchers
        max_num_threads: Maximum number of threads

    Returns:
        Tile
    """
    if len(tile_fetchers) == 1:
        max_num_threads = 1

    if max_num_threads == 1:
        tiles = [
            tile_fetcher(coordinates=coordinates)
            for tile_fetcher in tile_fetchers
        ]
        return Tile.from_tiles(
            tiles=tiles,
            copy=False,
        )

    with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
        tiles = list(executor.map(lambda tile_fetcher: tile_fetcher(coordinates=coordinates), tile_fetchers))

    return Tile.from_tiles(
        tiles=tiles,
        copy=False,
    )


def vrt_fetcher(
    coordinates: Coordinates,
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
    fill_value: int = 0,
) -> Tile:
    """Fetches a tile from the virtual raster.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of the tile in meters
        path: Path to the virtual raster (.vrt file)
        channel_keys: Channel name, channel name and time step combination, channel names,
            or channel name and time step combinations (if None, the channel is ignored)
        tile_size: Tile size in meters
        ground_sampling_distance: Ground sampling distance in meters
        interpolation_mode: Interpolation mode (`BILINEAR` or `NEAREST`)
        buffer_size: Buffer size in meters
        fill_value: Fill value of no-data pixels

    Returns:
        Tile
    """
    x_min, y_min = coordinates
    x_max = x_min + tile_size
    y_max = y_min + tile_size
    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )
    bounding_box = bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=False,
    )
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    with rio.open(path) as src:
        window = rio.windows.from_bounds(
            left=bounding_box.x_min,
            bottom=bounding_box.y_min,
            right=bounding_box.x_max,
            top=bounding_box.y_max,
            transform=src.transform,
        )
        data = src.read(
            window=window,
            out_shape=(src.count, tile_size_pixels, tile_size_pixels),
            boundless=True,
            resampling=interpolation_mode.to_rio(),
            fill_value=fill_value,
        )

    data = _permute_data(
        data=data,
    )
    return Tile.from_composite_raster(
        data=data,
        channel_keys=channel_keys,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
        copy=False,
    )


def wms_fetcher(
    coordinates: Coordinates,
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
    fill_value: str = '0x000000',
) -> Tile:
    """Fetches a tile from the web map service.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of the tile in meters
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
        fill_value: Fill value of no-data pixels

    Returns:
        Tile
    """
    x_min, y_min = coordinates
    x_max = x_min + tile_size
    y_max = y_min + tile_size
    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )
    bounding_box = bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=False,
    )
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    params = _get_wms_params(
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        tile_size_pixels=tile_size_pixels,
        bounding_box=bounding_box,
        style=style,
        fill_value=fill_value,
    )
    data = _request_wms(
        url=url,
        params=params,
    )

    data = _permute_data(
        data=data,
    )
    return Tile.from_composite_raster(
        data=data,
        channel_keys=channel_keys,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
        copy=False,
    )


def _compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
) -> TileSize:
    """Computes the tile size in pixels.

    Parameters:
        tile_size: Tile size in meters
        ground_sampling_distance: Ground sampling distance in meters

    Returns:
        Tile size in pixels

    Raises:
        AviaryUserError: Invalid `tile_size` (the tile size does not match the spatial extent of the data,
            resulting in a fractional number of pixels)
    """
    tile_size_pixels = (tile_size + 2 * buffer_size) / ground_sampling_distance

    if not tile_size_pixels.is_integer():
        message = (
            'Invalid tile_size! '
            'The tile size must match the spatial extent of the data, '
            'resulting in a whole number of pixels.'
        )
        raise AviaryUserError(message)

    return int(tile_size_pixels)


def _get_wms_params(
    version: WMSVersion,
    layer: str,
    epsg_code: EPSGCode,
    response_format: str,
    tile_size_pixels: int,
    bounding_box: BoundingBox,
    style: str | None = None,
    fill_value: str = '0x000000',
) -> dict[str, str]:
    """Returns the parameters of the request to the web map service.

    Parameters:
        version: Version of the web map service (`V1_1_1` or `V1_3_0`)
        layer: Layer
        epsg_code: EPSG code
        response_format: Format of the response (MIME type, e.g., 'image/png')
        tile_size_pixels: Tile size in pixels
        bounding_box: Bounding box
        style: Style
        fill_value: Fill value of no-data pixels

    Returns:
        Params

    Raises:
        AviaryUserError: Invalid `version`
    """
    params = {
        'service': 'WMS',
        'version': version.value,
        'request': 'GetMap',
        'layers': layer,
        'format': response_format,
        'width': str(tile_size_pixels),
        'height': str(tile_size_pixels),
        'bbox': ','.join(map(str, bounding_box)),
        'styles': '',
        'transparent': 'false',
        'bgcolor': fill_value,
    }

    if version == WMSVersion.V1_1_1:
        params['srs'] = f'EPSG:{epsg_code}'
    elif version == WMSVersion.V1_3_0:
        params['crs'] = f'EPSG:{epsg_code}'
    else:
        message = 'Invalid version!'
        raise AviaryUserError(message)

    if style is not None:
        params['styles'] = style

    return params


def _permute_data(
    data: npt.NDArray,
) -> npt.NDArray:
    """Permutes the data from channels-first to channels-last.

    Parameters:
        data: Data

    Returns:
        Data
    """
    return np.transpose(data, (1, 2, 0))


def _request_wms(
    url: str,
    params: dict[str, str],
) -> npt.NDArray:
    """Requests the web map service.

    Parameters:
        url: URL of the web map service
        params: Parameters of the request

    Returns:
        Data

    Raises:
        AviaryUserError: Invalid request (the response is not an image)
        AviaryUserError: Invalid request (the response is not in shape (n, n, 3) and data type uint8)
    """
    response = requests.get(
        url=url,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    if not response.headers['Content-Type'].startswith('image/'):
        message = (
            'Invalid request! '
            'The response must be an image.'
        )
        raise AviaryUserError(message)

    with rio.io.MemoryFile(response.content) as file, warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=rio.errors.NotGeoreferencedWarning)

        with file.open() as src:
            data = src.read()

            if data.ndim != 3:  # noqa: PLR2004
                message = (
                    'Invalid request! '
                    'The response must be in shape (n, n, 3) and data type uint8.'
                )
                raise AviaryUserError(message)

            conditions = [
                data.shape[0] != 3,  # noqa: PLR2004
                data.dtype != np.uint8,
            ]

            if any(conditions):
                message = (
                    'Invalid request! '
                    'The response must be in shape (n, n, 3) and data type uint8.'
                )
                raise AviaryUserError(message)

    return data
