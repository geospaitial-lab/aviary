#  Copyright (C) 2024-2026 Marius Maryniak
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

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio as rio

from aviary.core.grid import Grid

if TYPE_CHECKING:
    from aviary.core.channel import VectorChannel
    from aviary.core.enums import ChannelName
    from aviary.core.tiles import Tiles
    from aviary.core.type_aliases import EPSGCode


def grid_exporter(
    tiles: Tiles,
    path: Path,
) -> Tiles:
    """Exports the grid of the tiles.

    Parameters:
        tiles: Tiles
        path: Path to the JSON file (.json file)

    Returns:
        Tiles
    """
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size

    try:
        with path.open() as file:
            json_string = file.read()

        grid = Grid.from_json(json_string=json_string)
    except FileNotFoundError:
        grid = Grid(
            coordinates=None,
            tile_size=tile_size,
        )

    grid = grid.append(coordinates=coordinates)
    json_string = grid.to_json()

    with path.open('w') as file:
        file.write(json_string)

    return tiles


def raster_exporter(
    tiles: Tiles,
    channel_names:
        ChannelName | str |
        list[ChannelName | str],
    epsg_code: EPSGCode,
    path: Path,
    remove_channels: bool = True,
    max_num_threads: int | None = None,
) -> Tiles:
    """Exports the raster channels.

    Parameters:
        tiles: Tiles
        channel_names: Channel name or channel names
        epsg_code: EPSG code
        path: Path to the directory
        remove_channels: If True, the channels are removed
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
    data = tiles.to_composite_raster(
        channel_names=channel_names,
    )

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not isinstance(channel_names, list):
        channel_names = [channel_names]

    channel_names_repr = '_'.join(str(name) for name in channel_names)

    batch_size = tiles.batch_size
    tile_size = tiles.tile_size

    epsg_code = f'EPSG:{epsg_code}'

    def _write_data_item(index: int) -> None:
        x_min, y_min = tiles.coordinates[index]
        data_item = data[index]
        h, w, c = data_item.shape

        resolution = tile_size / w
        transform = rio.transform.from_origin(
            west=x_min,
            north=y_min + h * resolution,
            xsize=resolution,
            ysize=resolution,
        )

        profile = {
            'driver': 'GTiff',
            'height': h,
            'width': w,
            'count': c,
            'dtype': data_item.dtype,
            'crs': epsg_code,
            'transform': transform,
            'tiled': True,
            'blockxsize': 256,
            'blockysize': 256,
            'compress': 'deflate',
            'bigtiff': 'IF_SAFER',
        }

        filename = f'{channel_names_repr}_{x_min}_{y_min}.tiff'
        out_path = path / filename

        with rio.open(out_path, mode='w', **profile) as dst:
            data_item = np.transpose(data_item, (2, 0, 1))
            dst.write(data_item)

    if batch_size == 1:
        max_num_threads = 1

    if max_num_threads == 1:
        for index in range(batch_size):
            _write_data_item(index)
    else:
        with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
            list(executor.map(_write_data_item, range(batch_size)))

    if remove_channels:
        tiles = tiles.remove(
            channel_names=channel_names,
            inplace=True,
        )

    return tiles


def vector_exporter(
    tiles: Tiles,
    channel_name: ChannelName | str,
    epsg_code: EPSGCode,
    path: Path,
    remove_channel: bool = True,
) -> Tiles:
    """Exports the vector channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        epsg_code: EPSG code
        path: Path to the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed

    Returns:
        Tiles
    """
    channel: VectorChannel = tiles[channel_name]
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size
    data = channel.to_denormalized_data(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    data = pd.concat(
        data,
        ignore_index=True,
        copy=False,
    )
    epsg_code = f'EPSG:{epsg_code}'
    gdf = gpd.GeoDataFrame(data=data)

    if not gdf.empty:
        gdf = gdf.set_crs(
            crs=epsg_code,
            inplace=True,
        )

        gdf.to_file(
            path,
            driver='GPKG',
            mode='a',
        )

    if remove_channel:
        tiles = tiles.remove(
            channel_names=channel_name,
            inplace=True,
        )

    return tiles
