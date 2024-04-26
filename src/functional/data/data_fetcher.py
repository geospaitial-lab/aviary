from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.windows

from src.utils.types import (
    BoundingBox,
    BufferSize,
    GroundSamplingDistance,
    InterpolationMode,
    TileSize,
    XMin,
    YMin,
)


def vrt_data_fetcher(
    x_min: XMin,
    y_min: YMin,
    path: Path,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
    buffer_size: BufferSize = None,
    drop_channels: list[int] = None,
    fill_value: int = 0,
) -> npt.NDArray:
    """
    | Fetches the data from the VRT file.

    :param x_min: minimum x coordinate
    :param y_min: minimum y coordinate
    :param path: path to the VRT file
    :param tile_size: tile size in meters
    :param ground_sampling_distance: ground sampling distance in meters
    :param interpolation_mode: interpolation mode (InterpolationMode.BILINEAR or InterpolationMode.NEAREST)
    :param buffer_size: buffer size in meters
    :param drop_channels: channel indices to drop
    :param fill_value: fill value of nodata pixels
    :return: data
    """
    x_min, y_min, x_max, y_max = _compute_bounding_box(
        x_min=x_min,
        y_min=y_min,
        tile_size=tile_size,
        buffer_size=buffer_size,
    )
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    with rio.open(path) as src:
        window = rio.windows.from_bounds(
            left=x_min,
            bottom=y_min,
            right=x_max,
            top=y_max,
            transform=src.transform,
        )
        data = src.read(
            window=window,
            out_shape=(src.count, tile_size_pixels, tile_size_pixels),
            resampling=interpolation_mode.to_rio(),
            fill_value=fill_value,
        )

    data = _permute_data(
        data=data,
    )
    data = _drop_channels(
        data=data,
        drop_channels=drop_channels,
    )
    return data


def _compute_bounding_box(
    x_min: XMin,
    y_min: YMin,
    tile_size: TileSize,
    buffer_size: BufferSize | None,
) -> BoundingBox:
    """
    | Computes the bounding box of the tile.

    :param x_min: minimum x coordinate
    :param y_min: minimum y coordinate
    :param tile_size: tile size in meters
    :param buffer_size: buffer size in meters
    :return: bounding box (x_min, y_min, x_max, y_max) of the tile
    """
    if buffer_size is None:
        return (
            x_min,
            y_min,
            x_min + tile_size,
            y_min + tile_size,
        )

    return (
        x_min - buffer_size,
        y_min - buffer_size,
        x_min + tile_size + buffer_size,
        y_min + tile_size + buffer_size,
    )


def _compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize | None,
    ground_sampling_distance: GroundSamplingDistance,
) -> int:
    """
    | Computes the tile size in pixels.

    :param tile_size: tile size in meters
    :param ground_sampling_distance: ground sampling distance in meters
    :return: tile size in pixels
    """
    if buffer_size is None:
        return int(tile_size / ground_sampling_distance)

    return int((tile_size + 2 * buffer_size) / ground_sampling_distance)


def _drop_channels(
    data: npt.NDArray,
    drop_channels: list[int] | None,
) -> npt.NDArray:
    """
    | Drops the specified channels from the data.

    :param data: data
    :param drop_channels: channel indices to drop
    :return: data
    """
    if drop_channels is None:
        return data

    channels = np.arange(data.shape[-1])
    keep_channels = np.delete(channels, drop_channels)
    return data[..., keep_channels]


def _permute_data(
    data: npt.NDArray,
) -> npt.NDArray:
    """
    | Permutes the data from channels-first to channels-last.

    :param data: data
    :return: data
    """
    return np.transpose(data, (1, 2, 0))
