from __future__ import annotations

import warnings
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from typing import (
    TYPE_CHECKING,
    Literal,
)

if TYPE_CHECKING:
    from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.windows
import requests

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import (
    InterpolationMode,
    WMSVersion,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.tile import Tile

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        Channels,
        ChannelsSet,
        Coordinates,
        EPSGCode,
        GroundSamplingDistance,
        TileSize,
    )
    from aviary.inference.tile_fetcher import TileFetcher


def composite_fetcher(
    coordinates: Coordinates,
    tile_fetchers: list[TileFetcher],
    axis: Literal['channel', 'time_step'] = 'channel',
    num_workers: int = 1,
) -> Tile:
    """Fetches a tile from the sources.

    Parameters:
        coordinates: coordinates (x_min, y_min) of the tile
        tile_fetchers: tile fetchers
        axis: axis to concatenate the tiles (`channel`, `time_step`)
        num_workers: number of workers

    Returns:
        tile
    """
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        tasks = [
            executor.submit(
                tile_fetcher,
                coordinates=coordinates,
            )
            for tile_fetcher in tile_fetchers
        ]
        tiles = [
            futures.result() for futures in as_completed(tasks)
        ]

    return Tile.from_tiles(
        tiles=tiles,
        axis=axis,
    )


def vrt_fetcher(
    coordinates: Coordinates,
    path: Path,
    channels: Channels,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
    buffer_size: BufferSize = 0,
    ignore_channels: ChannelsSet | None = None,
    fill_value: int = 0,
) -> Tile:
    """Fetches a tile from the virtual raster.

    Parameters:
        coordinates: coordinates (x_min, y_min) of the tile
        path: path to the virtual raster (.vrt file)
        channels: channels
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        interpolation_mode: interpolation mode (`BILINEAR` or `NEAREST`)
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        ignore_channels: channels to ignore
        fill_value: fill value of nodata pixels

    Returns:
        tile
    """
    x_min, y_min = coordinates
    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_min + tile_size,
        y_max=y_min + tile_size,
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
    tile = Tile.from_composite(
        data=data,
        channels=channels,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
    )

    if ignore_channels is not None:
        for channel in ignore_channels:
            tile = tile.remove_channel(
                channel=channel,
                inplace=True,
            )

    return tile


def wms_fetcher(
    coordinates: Coordinates,
    url: str,
    version: WMSVersion,
    layer: str,
    epsg_code: EPSGCode,
    response_format: str,
    channels: Channels,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    style: str | None = None,
    buffer_size: BufferSize = 0,
    ignore_channels: ChannelsSet | None = None,
    fill_value: str = '0x000000',
) -> Tile:
    """Fetches a tile from the web map service.

    Parameters:
        coordinates: coordinates (x_min, y_min) of the tile
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
        fill_value: fill value of nodata pixels

    Returns:
        tile
    """
    x_min, y_min = coordinates
    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_min + tile_size,
        y_max=y_min + tile_size,
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
    tile = Tile.from_composite(
        data=data,
        channels=channels,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
    )

    if ignore_channels is not None:
        for channel in ignore_channels:
            tile = tile.remove_channel(
                channel=channel,
                inplace=True,
            )

    return tile


def _compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
) -> int:
    """Computes the tile size in pixels.

    Parameters:
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters

    Returns:
        tile size in pixels
    """
    if buffer_size == 0:
        return int(tile_size / ground_sampling_distance)

    return int((tile_size + 2 * buffer_size) / ground_sampling_distance)


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
        version: version of the web map service (`V1_1_1` or `V1_3_0`)
        layer: name of the layer
        epsg_code: EPSG code
        response_format: format of the response (MIME type, e.g., 'image/png')
        tile_size_pixels: tile size in pixels
        bounding_box: bounding box
        style: name of the style
        fill_value: fill value of nodata pixels

    Returns:
        params

    Raises:
        AviaryUserError: Invalid WMS version
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
        message = 'Invalid WMS version!'
        raise AviaryUserError(message)

    if style is not None:
        params['styles'] = style

    return params


def _permute_data(
    data: npt.NDArray,
) -> npt.NDArray:
    """Permutes the data from channels-first to channels-last.

    Parameters:
        data: data

    Returns:
        data
    """
    return np.transpose(data, (1, 2, 0))


def _request_wms(
    url: str,
    params: dict[str, str],
) -> npt.NDArray:
    """Requests the web map service.

    Parameters:
        url: url of the web map service
        params: parameters of the request

    Returns:
        data

    Raises:
        AviaryUserError: Invalid request (response is not an image)
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

            conditions = [
                data.ndim != 3,  # noqa: PLR2004
                data.shape[0] != 3,  # noqa: PLR2004
                data.dtype != np.uint8,
            ]

            if any(conditions):
                message = (
                    'Invalid request! '
                    'The response must be an array of shape (n, n, 3) and data type uint8.'
                )
                raise AviaryUserError(message)

    return data
