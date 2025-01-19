from __future__ import annotations

import warnings
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from typing import TYPE_CHECKING

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
from aviary.core.type_aliases import (
    BufferSize,
    Coordinate,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)

if TYPE_CHECKING:
    from aviary.data.data_fetcher import DataFetcher


def composite_fetcher(
    x_min: Coordinate,
    y_min: Coordinate,
    data_fetchers: list[DataFetcher],
    num_workers: int = 1,
) -> npt.NDArray:
    """Fetches data from the sources.

    Parameters:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        data_fetchers: data fetchers
        num_workers: number of workers

    Returns:
        data
    """
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        tasks = [
            executor.submit(
                data_fetcher,
                x_min=x_min,
                y_min=y_min,
            )
            for data_fetcher in data_fetchers
        ]
        data = [
            futures.result() for futures in as_completed(tasks)
        ]

    return np.concatenate(data, axis=-1)


def vrt_fetcher(
    x_min: Coordinate,
    y_min: Coordinate,
    path: Path,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
    buffer_size: BufferSize = 0,
    drop_channels: list[int] | None = None,
    fill_value: int = 0,
) -> npt.NDArray:
    """Fetches data from the virtual raster.

    Parameters:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        path: path to the virtual raster (.vrt file)
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        interpolation_mode: interpolation mode (`BILINEAR` or `NEAREST`)
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        drop_channels: channel indices to drop (supports negative indexing)
        fill_value: fill value of nodata pixels

    Returns:
        data
    """
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
    return _drop_channels(
        data=data,
        drop_channels=drop_channels,
    )


def wms_fetcher(
    x_min: Coordinate,
    y_min: Coordinate,
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
    fill_value: str = '0x000000',
) -> npt.NDArray:
    """Fetches data from the web map service.

    Parameters:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
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
        fill_value: fill value of nodata pixels

    Returns:
        data
    """
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
    return _drop_channels(
        data=data,
        drop_channels=drop_channels,
    )


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


def _drop_channels(
    data: npt.NDArray,
    drop_channels: list[int] | None,
) -> npt.NDArray:
    """Drops the specified channels from the data.

    Parameters:
        data: data
        drop_channels: channel indices to drop (supports negative indexing)

    Returns:
        data
    """
    if drop_channels is None:
        return data

    channels = np.arange(data.shape[-1])
    retain_channels = np.delete(channels, drop_channels)
    return data[..., retain_channels]


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
