#  Copyright (C) 2024-2026 Marius Maryniak
#  Copyright (C) 2026 Alexander Roß
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.features

from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import (
    ChannelName,
    Connectivity,
    DType,
    SlopeUnit,
    _coerce_channel_name,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.tiles import Tiles

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        ChannelNameSet,
        GroundSamplingDistance,
    )
    from aviary.tile.tiles_processor import TilesProcessor


def _process_data(
    tiles: Tiles,
    channel_name: ChannelName | str,
    process_data_item: Callable,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Processes the data of the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        process_data_item: Function to process each data item
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    new_channel_name = _coerce_channel_name(channel_name=new_channel_name)

    channel = tiles[channel_name]

    if new_channel_name is not None:
        channel = channel.copy()

    data = channel.data

    if len(channel) == 1:
        max_num_threads = 1

    if max_num_threads == 1:
        data = [
            process_data_item(data_item=data_item)
            for data_item in data
        ]
    else:
        with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
            data = list(executor.map(process_data_item, data))

    channel._data = data  # noqa: SLF001

    if new_channel_name is not None:
        channel.name = new_channel_name
        return tiles.append(
            channels=channel,
            inplace=True,
        )

    return tiles


def _compute_dem_gradients(
    digital_elevation_model: npt.NDArray,
    ground_sampling_distance: GroundSamplingDistance,
) -> tuple[npt.NDArray, npt.NDArray]:
    """Computes the digital elevation model gradients.

    References:
        - https://ieeexplore.ieee.org/document/1456186

    Parameters:
        digital_elevation_model: Digital elevation model
        ground_sampling_distance: Ground sampling distance in meters per pixel

    Returns:
        Gradients
    """
    z_north = digital_elevation_model[:-2, 1:-1]
    z_north_east = digital_elevation_model[:-2, 2:]
    z_east = digital_elevation_model[1:-1, 2:]
    z_south_east = digital_elevation_model[2:, 2:]
    z_south = digital_elevation_model[2:, 1:-1]
    z_south_west = digital_elevation_model[2:, :-2]
    z_west = digital_elevation_model[1:-1, :-2]
    z_north_west = digital_elevation_model[:-2, :-2]

    dz_dx = (
        ((z_north_east + 2 * z_east + z_south_east) - (z_north_west + 2 * z_west + z_south_west)) /
        (8 * ground_sampling_distance)
    )
    dz_dy = (
        ((z_north_east + 2 * z_north + z_north_west) - (z_south_east + 2 * z_south + z_south_west)) /
        (8 * ground_sampling_distance)
    )

    dz_dx = np.pad(dz_dx, ((1, 1), (1, 1)), mode='edge')
    dz_dy = np.pad(dz_dy, ((1, 1), (1, 1)), mode='edge')

    return dz_dx, dz_dy


def aspect_processor(
    tiles: Tiles,
    channel_name: ChannelName | str = ChannelName.DEM,
    new_channel_name: ChannelName | str = ChannelName.ASPECT,
    max_num_threads: int | None = None,
) -> Tiles:
    """Computes the aspect from the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _aspect_data_item(
            data_item=data_item,
            ground_sampling_distance=tiles[channel_name].ground_sampling_distance,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _aspect_data_item(
    data_item: npt.NDArray,
    ground_sampling_distance: GroundSamplingDistance,
) -> npt.NDArray:
    """Computes the aspect from the data item.

    Parameters:
        data_item: Data item
        ground_sampling_distance: Ground sampling distance in meters per pixel

    Returns:
        Data item
    """
    dz_dx, dz_dy = _compute_dem_gradients(
        digital_elevation_model=data_item,
        ground_sampling_distance=ground_sampling_distance,
    )

    return np.rad2deg(-(np.arctan2(dz_dy, dz_dx) + (np.pi / 2)) % (2 * np.pi))


def cast_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    dtype: DType,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Casts the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        dtype: Data type
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _cast_data_item(
            data_item=data_item,
            dtype=dtype,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _cast_data_item(
    data_item: npt.NDArray,
    dtype: DType,
) -> npt.NDArray:
    """Casts the data item.

    Parameters:
        data_item: Data item
        dtype: Data type

    Returns:
        Data item
    """
    return data_item.astype(dtype.to_numpy())


def copy_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    new_channel_name: ChannelName | str | None = None,
) -> Tiles:
    """Copies the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        new_channel_name: New channel name

    Returns:
        Tiles
    """
    new_channel_name = _coerce_channel_name(channel_name=new_channel_name)

    if new_channel_name is None:
        return tiles

    channel = tiles[channel_name]
    channel = channel.copy()

    channel.name = new_channel_name
    return tiles.append(
        channels=channel,
        inplace=True,
    )


_NUMEXPR_CACHE: dict[str, object] = {}


def expression_processor(
    tiles: Tiles,
    expression_string: str,
    new_channel_name: ChannelName | str,
    dtype: DType | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Computes the new channel from the expression.

    Parameters:
        tiles: Tiles
        expression_string: Expression string based on the numexpr expression syntax
        new_channel_name: New channel name
        dtype: Data type
        max_num_threads: Maximum number of threads

    Returns:
        Tiles

    Raises:
        AviaryUserError: Invalid `expression_string` (the expression string contains no channel names)
    """
    try:
        import numexpr as ne  # noqa: PLC0415
    except ImportError as error:
        message = (
            'Missing dependencies! '
            'To use ExpressionProcessor, you need to install the '
            'expression dependency group (pip install geospaitial-lab-aviary[expression]).'
        )
        raise ImportError(message) from error

    new_channel_name = _coerce_channel_name(channel_name=new_channel_name)

    expression_string = expression_string.strip()
    compiled = _NUMEXPR_CACHE.get(expression_string)

    if compiled is None:
        compiled = ne.NumExpr(expression_string)
        _NUMEXPR_CACHE[expression_string] = compiled

    channel_names = list(compiled.input_names)

    if not channel_names:
        message = (
            'Invalid expression_string! '
            'The expression string must contain at least one channel name.'
        )
        raise AviaryUserError(message)

    batch_size = tiles.batch_size

    def _compute_data_item(index: int) -> npt.NDArray:
        channels_dict = {
            channel_name: tiles[_coerce_channel_name(channel_name=channel_name)][index]
            for channel_name in channel_names
        }
        args = [
            channels_dict[channel_name]
            for channel_name in channel_names
        ]

        data_item = compiled(*args)

        if dtype is not None:
            data_item = data_item.astype(dtype.to_numpy())

        return data_item

    data: list[npt.NDArray] = []

    if batch_size == 1:
        max_num_threads = 1

    if max_num_threads == 1:
        data = [
            _compute_data_item(index)
            for index in range(batch_size)
        ]
    else:
        with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
            data = list(executor.map(_compute_data_item, range(batch_size)))

    first_channel = tiles[_coerce_channel_name(channel_name=channel_names[0])]
    buffer_size = first_channel.buffer_size

    channel = RasterChannel(
        data=data,
        name=new_channel_name,
        buffer_size=buffer_size,
        copy=False,
    )

    return tiles.append(
        channels=channel,
        inplace=True,
    )


def hillshade_processor(
    tiles: Tiles,
    channel_name: ChannelName | str | None = ChannelName.DEM,
    slope_channel_name: ChannelName | str | None = None,
    aspect_channel_name: ChannelName | str | None = None,
    azimuth: float = 315.,
    altitude: float = 45.,
    new_channel_name: ChannelName | str = ChannelName.HILLSHADE,
    max_num_threads: int | None = None,
) -> Tiles:
    """Computes the hillshade from the channel or channels.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        slope_channel_name: Channel name of the slope channel
        aspect_channel_name: Channel name of the aspect channel
        azimuth: Angle to north of the light source in degrees
        altitude: Angle to the horizontal plane of the light source in degrees
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles

    Raises:
        AviaryUserError: Invalid `channel_name` (neither the channel name nor
            the slope channel name and aspect channel name are specified)
    """
    if channel_name is not None:
        return _process_data(
            tiles=tiles,
            channel_name=channel_name,
            process_data_item=lambda data_item: _hillshade_dem_data_item(
                data_item=data_item,
                ground_sampling_distance=tiles[channel_name].ground_sampling_distance,
                azimuth=azimuth,
                altitude=altitude,
            ),
            new_channel_name=new_channel_name,
            max_num_threads=max_num_threads,
        )

    if slope_channel_name is not None and aspect_channel_name is not None:
        new_channel_name = _coerce_channel_name(channel_name=new_channel_name)

        channel = tiles[slope_channel_name].copy()

        slope_data = tiles[slope_channel_name].data
        aspect_data = tiles[aspect_channel_name].data

        if len(channel) == 1:
            max_num_threads = 1

        if max_num_threads == 1:
            data = [
                _hillshade_slope_aspect_data_item(
                    slope_data_item=slope_data_item,
                    aspect_data_item=aspect_data_item,
                    azimuth=azimuth,
                    altitude=altitude,
                )
                for slope_data_item, aspect_data_item in zip(slope_data, aspect_data, strict=False)
            ]
        else:
            with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
                data = list(executor.map(
                    _hillshade_slope_aspect_data_item,
                    slope_data,
                    aspect_data,
                    repeat(azimuth),
                    repeat(altitude),
                ))

        channel._data = data  # noqa: SLF001
        channel.name = new_channel_name

        return tiles.append(
            channels=channel,
            inplace=True,
        )

    message = (
        'Invalid channel_name! '
        'Either the channel name or the slope channel name and aspect channel name must be specified.'
    )
    raise AviaryUserError(message)


def _hillshade_slope_aspect_data_item(
    slope_data_item: npt.NDArray,
    aspect_data_item: npt.NDArray,
    azimuth: float = 315.,
    altitude: float = 45.,
) -> npt.NDArray:
    """Computes the hillshade from the slope and aspect data items.

    Parameters:
        slope_data_item: Slope data item
        aspect_data_item: Aspect data item
        azimuth: Angle to north of the light source in degrees
        altitude: Angle to the horizontal plane of the light source in degrees

    Returns:
        Data item
    """
    slope_rad = np.deg2rad(slope_data_item)
    aspect_rad = np.deg2rad(aspect_data_item)
    azimuth_rad = np.deg2rad(azimuth)
    zenith_rad = np.deg2rad(90 - altitude)

    illumination = (
        np.cos(zenith_rad) * np.cos(slope_rad) +
        np.sin(zenith_rad) * np.sin(slope_rad) * np.cos(azimuth_rad - aspect_rad)
    )
    hillshade = 255 * illumination

    return np.clip(hillshade, 0.0, 255.0).astype(np.uint8)


def _hillshade_dem_data_item(
    data_item: npt.NDArray,
    ground_sampling_distance: GroundSamplingDistance,
    azimuth: float = 315.,
    altitude: float = 45.,
) -> npt.NDArray:
    """Computes the hillshade from the digital elevation model data item.

    Parameters:
        data_item: Data item
        ground_sampling_distance: Ground sampling distance in meters per pixel
        azimuth: Angle to north of the light source in degrees
        altitude: Angle to the horizontal plane of the light source in degrees

    Returns:
        Data item
    """
    dz_dx, dz_dy = _compute_dem_gradients(data_item, ground_sampling_distance)
    slope_data_item = np.sqrt(dz_dx ** 2 + dz_dy ** 2)
    slope_data_item = np.rad2deg(np.arctan(slope_data_item))
    aspect_data_item = np.rad2deg(-(np.arctan2(dz_dy, dz_dx) + (np.pi / 2)) % (2 * np.pi))

    return _hillshade_slope_aspect_data_item(
        slope_data_item=slope_data_item,
        aspect_data_item=aspect_data_item,
        azimuth=azimuth,
        altitude=altitude,
    )


def normalize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    min_value: float,
    max_value: float,
    dtype: DType | None = DType.FLOAT32,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Normalizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        min_value: Minimum value
        max_value: Maximum value
        dtype: Data type
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _normalize_data_item(
            data_item=data_item,
            min_value=min_value,
            max_value=max_value,
            dtype=dtype,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _normalize_data_item(
    data_item: npt.NDArray,
    min_value: float,
    max_value: float,
    dtype: DType | None = DType.FLOAT32,
) -> npt.NDArray:
    """Normalizes the data item.

    Parameters:
        data_item: Data item
        min_value: Minimum value
        max_value: Maximum value
        dtype: Data type

    Returns:
        Data item
    """
    data_item = (data_item - min_value) / (max_value - min_value)

    if dtype is not None:
        data_item = data_item.astype(dtype.to_numpy())

    return data_item


def parallel_composite_processor(
    tiles: Tiles,
    tiles_processors: list[TilesProcessor],
) -> Tiles:
    """Processes the tiles with each tiles processor.

    Parameters:
        tiles: Tiles
        tiles_processors: Tiles processors

    Returns:
        Tiles
    """
    tiles = [
        tiles_processor(tiles=tiles.copy())
        for tiles_processor in tiles_processors
    ]
    return Tiles.from_tiles(
        tiles=tiles,
        copy=False,
    )


def rasterize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    field: str,
    ground_sampling_distance: GroundSamplingDistance,
    mapping: dict[object, int] | None = None,
    background_value: int = 0,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Rasterizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        field: Field
        ground_sampling_distance: Ground sampling distance in meters per pixel
        mapping: Mapping of the values
        background_value: Background value
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    tile_size = tiles.tile_size
    buffer_size = tiles[channel_name].buffer_size * tile_size

    tile_size_pixels = (tile_size + 2 * buffer_size) / ground_sampling_distance

    if not tile_size_pixels.is_integer():
        message = (
            'Invalid tile_size! '
            'The tile size must match the spatial extent of the data, '
            'resulting in a whole number of pixels.'
        )
        raise AviaryUserError(message)

    tile_size_pixels = int(tile_size_pixels)

    tiles = _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _rasterize_data_item(
            data_item=data_item,
            field=field,
            tile_size_pixels=tile_size_pixels,
            mapping=mapping,
            background_value=background_value,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )

    if new_channel_name is not None:  # noqa: SIM108
        channel = tiles[new_channel_name]
    else:
        channel = tiles[channel_name]

    channel = RasterChannel(
        data=channel.data,
        name=channel.name,
        buffer_size=channel.buffer_size,
        copy=False,
    )

    if new_channel_name is not None:
        tiles = tiles.remove(
            channel_names=new_channel_name,
            inplace=True,
        )
        tiles = tiles.append(
            channels=channel,
            inplace=True,
        )
    else:
        tiles = tiles.remove(
            channel_names=channel_name,
            inplace=True,
        )
        tiles = tiles.append(
            channels=channel,
            inplace=True,
        )

    return tiles


def _rasterize_data_item(
    data_item: gpd.GeoDataFrame,
    field: str,
    tile_size_pixels: int,
    mapping: dict[object, int] | None = None,
    background_value: int = 0,
) -> npt.NDArray:
    """Rasterizes the data item.

    Parameters:
        data_item: Data item
        field: Field
        tile_size_pixels: Tile size in pixels
        mapping: Mapping of the values
        background_value: Background value

    Returns:
        Data item
    """
    x_min = 0.
    y_min = 0.
    x_max = 1.
    y_max = 1.

    transform = rio.transform.from_bounds(
        west=x_min,
        south=y_min,
        east=x_max,
        north=y_max,
        width=tile_size_pixels,
        height=tile_size_pixels,
    )

    if data_item.empty:
        shapes = []
    else:
        geometries = data_item.geometry
        values = data_item[field]

        if mapping is not None:
            values = values.map(mapping)

        shapes = [
            (geometry, int(values))
            for geometry, values in zip(geometries, values, strict=False)
        ]

    return rio.features.rasterize(
        shapes=shapes,
        out_shape=(tile_size_pixels, tile_size_pixels),
        fill=background_value,
        transform=transform,
    )


def remove_buffer_processor(
    tiles: Tiles,
    channel_names:
        ChannelName | str |
        ChannelNameSet |
        bool |
        None = True,
) -> Tiles:
    """Removes the buffer of the channels.

    Parameters:
        tiles: Tiles
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.remove_buffer(
        channel_names=channel_names,
        inplace=True,
    )


def remove_processor(
    tiles: Tiles,
    channel_names:
        ChannelName | str |
        ChannelNameSet |
        bool |
        None = True,
) -> Tiles:
    """Removes the channels.

    Parameters:
        tiles: Tiles
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.remove(
        channel_names=channel_names,
        inplace=True,
    )


def select_processor(
    tiles: Tiles,
    channel_names:
        ChannelName | str |
        ChannelNameSet |
        bool |
        None = True,
) -> Tiles:
    """Selects the channels.

    Parameters:
        tiles: Tiles
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.select(
        channel_names=channel_names,
        inplace=True,
    )


def sequential_composite_processor(
    tiles: Tiles,
    tiles_processors: list[TilesProcessor],
) -> Tiles:
    """Processes the tiles with each tiles processor.

    Parameters:
        tiles: Tiles
        tiles_processors: Tiles processors

    Returns:
        Tiles
    """
    for tiles_processor in tiles_processors:
        tiles = tiles_processor(tiles=tiles)

    return tiles


def sieve_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    threshold: int,
    connectivity: Connectivity = Connectivity.FOUR,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Sieves the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        threshold: Threshold (the minimum area of the polygon to retain) in pixels
        connectivity: Connectivity (`FOUR` or `EIGHT`)
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _sieve_data_item(
            data_item=data_item,
            threshold=threshold,
            connectivity=connectivity,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _sieve_data_item(
    data_item: npt.NDArray,
    threshold: int,
    connectivity: Connectivity = Connectivity.FOUR,
) -> npt.NDArray:
    """Sieves the data item.

    Parameters:
        data_item: Data item
        threshold: Threshold (the minimum area of the polygon to retain) in pixels
        connectivity: Connectivity (`FOUR` or `EIGHT`)

    Returns:
        Data item
    """
    return rio.features.sieve(
        source=data_item,
        size=threshold,
        connectivity=connectivity.value,
    )


def slope_processor(
    tiles: Tiles,
    channel_name: ChannelName | str = ChannelName.DEM,
    unit: SlopeUnit = SlopeUnit.DEGREES,
    new_channel_name: ChannelName | str = ChannelName.SLOPE,
    max_num_threads: int | None = None,
) -> Tiles:
    """Computes the slope from the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        unit: Unit of the slope (`DEGREES` or `PERCENT`)
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _slope_data_item(
            data_item=data_item,
            ground_sampling_distance=tiles[channel_name].ground_sampling_distance,
            unit=unit,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _slope_data_item(
    data_item: npt.NDArray,
    ground_sampling_distance: GroundSamplingDistance,
    unit: SlopeUnit = SlopeUnit.DEGREES,
) -> npt.NDArray:
    """Computes the slope from the data item.

    Parameters:
        data_item: Data item
        ground_sampling_distance: Ground sampling distance in meters per pixel
        unit: Unit of the slope (`DEGREES` or `PERCENT`)

    Returns:
        Data item

    Raises:
        AviaryUserError: Invalid `unit`
    """
    dz_dx, dz_dy = _compute_dem_gradients(
        digital_elevation_model=data_item,
        ground_sampling_distance=ground_sampling_distance,
    )

    data_item = np.sqrt(dz_dx ** 2 + dz_dy ** 2)

    if unit == SlopeUnit.DEGREES:
        return np.rad2deg(np.arctan(data_item))

    if unit == SlopeUnit.PERCENT:
        return 100. * data_item

    message = 'Invalid unit!'
    raise AviaryUserError(message)


def standardize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    mean_value: float,
    std_value: float,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Standardizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        mean_value: Mean value
        std_value: Standard deviation value
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    return _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _standardize_data_item(
            data_item=data_item,
            mean_value=mean_value,
            std_value=std_value,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _standardize_data_item(
    data_item: npt.NDArray,
    mean_value: float,
    std_value: float,
) -> npt.NDArray:
    """Standardizes the data item.

    Parameters:
        data_item: Data item
        mean_value: Mean value
        std_value: Standard deviation value

    Returns:
        Data item
    """
    data_item = (data_item - mean_value) / std_value

    if data_item.dtype != np.float32:
        data_item = data_item.astype(np.float32)

    return data_item


def stub_processor(
    tiles: Tiles,
    delay: float = 0.,
    jitter: float = 0.,
) -> Tiles:
    """Passes through the tiles.

    Parameters:
        tiles: Tiles
        delay: Delay in seconds
        jitter: Jitter in seconds

    Returns:
        Tiles
    """
    sleep = max(0., delay + random.uniform(-jitter, jitter))  # noqa: S311
    time.sleep(sleep)
    return tiles


def vectorize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    field: str,
    background_value: int | None = None,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Vectorizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        field: Field
        background_value: Background value
        new_channel_name: New channel name
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    tiles = _process_data(
        tiles=tiles,
        channel_name=channel_name,
        process_data_item=lambda data_item: _vectorize_data_item(
            data_item=data_item,
            field=field,
            background_value=background_value,
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )

    if new_channel_name is not None:  # noqa: SIM108
        channel = tiles[new_channel_name]
    else:
        channel = tiles[channel_name]

    channel = VectorChannel(
        data=channel.data,
        name=channel.name,
        buffer_size=channel.buffer_size,
        copy=False,
    )

    if new_channel_name is not None:
        tiles = tiles.remove(
            channel_names=new_channel_name,
            inplace=True,
        )
        tiles = tiles.append(
            channels=channel,
            inplace=True,
        )
    else:
        tiles = tiles.remove(
            channel_names=channel_name,
            inplace=True,
        )
        tiles = tiles.append(
            channels=channel,
            inplace=True,
        )

    return tiles


def _vectorize_data_item(
    data_item: npt.NDArray,
    field: str,
    background_value: int | None = None,
) -> npt.NDArray:
    """Vectorizes the data item.

    Parameters:
        data_item: Data item
        field: Field
        background_value: Background value

    Returns:
        Data item
    """
    x_min = 0.
    y_min = 0.
    x_max = 1.
    y_max = 1.
    tile_size = data_item.shape[0]

    transform = rio.transform.from_bounds(
        west=x_min,
        south=y_min,
        east=x_max,
        north=y_max,
        width=tile_size,
        height=tile_size,
    )

    features = [
        {
            'properties': {field: int(value)},
            'geometry': polygon,
        }
        for polygon, value
        in rio.features.shapes(
            source=data_item,
            transform=transform,
        )
        if background_value is None or int(value) != background_value
    ]

    if not features:
        return gpd.GeoDataFrame(data=[])

    return gpd.GeoDataFrame.from_features(features=features)
