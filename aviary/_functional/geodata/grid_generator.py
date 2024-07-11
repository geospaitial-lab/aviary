from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, box

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from aviary._utils.types import (
        BoundingBox,
        CoordinatesSet,
        EPSGCode,
        TileSize,
    )


def compute_coordinates(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    quantize: bool = True,
) -> CoordinatesSet:
    """Computes the coordinates of the bottom left corner of each tile.

    Parameters:
        bounding_box: bounding box
        tile_size: tile size in meters
        quantize: if True, the bounding box is quantized to `tile_size`

    Returns:
        coordinates (x_min, y_min) of each tile
    """
    if quantize:
        bounding_box = bounding_box.quantize(
            value=tile_size,
            inplace=False,
        )

    coordinates_range_x = np.arange(bounding_box.x_min, bounding_box.x_max, tile_size)
    coordinates_range_y = np.arange(bounding_box.y_min, bounding_box.y_max, tile_size)
    coordinates_x, coordinates_y = np.meshgrid(coordinates_range_x, coordinates_range_y)

    coordinates_x = coordinates_x.reshape(-1)[..., np.newaxis]
    coordinates_y = coordinates_y.reshape(-1)[..., np.newaxis]
    return np.concatenate((coordinates_x, coordinates_y), axis=-1).astype(np.int32)


def generate_grid(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    epsg_code: EPSGCode,
    quantize: bool = True,
) -> gpd.GeoDataFrame:
    """Generates a geodataframe of the grid.

    Parameters:
        bounding_box: bounding box
        tile_size: tile size in meters
        epsg_code: EPSG code
        quantize: if True, the bounding box is quantized to `tile_size`

    Returns:
        grid
    """
    coordinates = compute_coordinates(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    tiles = _generate_tiles(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    return gpd.GeoDataFrame(
        geometry=tiles,
        crs=f'EPSG:{epsg_code}',
    )


def _generate_tiles(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
) -> list[Polygon]:
    """Generates a list of tiles from the coordinates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters

    Returns:
        list of tiles
    """
    return [
        box(x_min, y_min, x_min + tile_size, y_min + tile_size)
        for x_min, y_min in coordinates
    ]
