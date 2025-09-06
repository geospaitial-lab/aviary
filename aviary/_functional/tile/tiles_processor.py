from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.features

from aviary.core.channel import VectorChannel
from aviary.core.enums import _coerce_channel_name
from aviary.core.tiles import Tiles

if TYPE_CHECKING:
    from aviary.core.enums import ChannelName
    from aviary.core.type_aliases import ChannelNameSet
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


def normalize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    min_value: float,
    max_value: float,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Normalizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        min_value: Minimum value
        max_value: Maximum value
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
        ),
        new_channel_name=new_channel_name,
        max_num_threads=max_num_threads,
    )


def _normalize_data_item(
    data_item: npt.NDArray,
    min_value: float,
    max_value: float,
) -> npt.NDArray:
    """Normalizes the data item.

    Parameters:
        data_item: Data item
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        Data item
    """
    data_item = (data_item - min_value) / (max_value - min_value)

    if data_item.dtype != np.float32:
        data_item = data_item.astype(np.float32)

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
        data_item.astype(np.float32)

    return data_item


def vectorize_processor(
    tiles: Tiles,
    channel_name: ChannelName | str,
    ignore_background_class: bool = True,
    new_channel_name: ChannelName | str | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Vectorizes the channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        ignore_background_class: If True, the background class (value 0) is not vectorized
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
            ignore_background_class=ignore_background_class,
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
    ignore_background_class: bool = True,
) -> npt.NDArray:
    """Vectorizes the data item.

    Parameters:
        data_item: Data item
        ignore_background_class: If True, the background class (value 0) is not vectorized

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
            'properties': {'class': int(value)},
            'geometry': polygon,
        }
        for polygon, value
        in rio.features.shapes(
            source=data_item,
            transform=transform,
        )
        if not ignore_background_class or int(value) != 0
    ]

    if not features:
        return gpd.GeoDataFrame(data=[])

    return gpd.GeoDataFrame.from_features(features=features)
