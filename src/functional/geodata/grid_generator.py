import geopandas as gpd
import numpy as np
from shapely.geometry import box, Polygon

from ...utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
    XMin,
    YMin,
)


def compute_coordinates(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    quantize: bool = True,
) -> Coordinates:
    """Computes the coordinates of the bottom left corner of each tile.

    Parameters:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
        tile_size: tile size in meters
        quantize: if True, the bounding box is quantized to `tile_size`

    Returns:
        coordinates (x_min, y_min) of each tile
    """
    x_min, y_min, x_max, y_max = bounding_box

    if quantize:
        x_min, y_min = _quantize_coordinates(
            x_min=x_min,
            y_min=y_min,
            tile_size=tile_size,
        )

    coordinates_range_x = np.arange(x_min, x_max, tile_size)
    coordinates_range_y = np.arange(y_min, y_max, tile_size)
    coordinates_x, coordinates_y = np.meshgrid(coordinates_range_x, coordinates_range_y)

    coordinates_x = coordinates_x.reshape(-1)[..., np.newaxis]
    coordinates_y = coordinates_y.reshape(-1)[..., np.newaxis]
    coordinates = np.concatenate((coordinates_x, coordinates_y), axis=-1).astype(np.int32)
    return coordinates


def _quantize_coordinates(
    x_min: XMin,
    y_min: YMin,
    tile_size: TileSize,
) -> tuple[XMin, YMin]:
    """Quantizes the coordinates of the bottom left corner of the bounding box to the tile size.

    Parameters:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        tile_size: tile size in meters

    Returns:
        quantized coordinates (x_min, y_min) of the bounding box
    """
    x_min = x_min - (x_min % tile_size)
    y_min = y_min - (y_min % tile_size)
    return x_min, y_min


def generate_grid(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    epsg_code: EPSGCode,
    quantize: bool = True,
) -> gpd.GeoDataFrame:
    """Generates a geodataframe of the grid.

    Parameters:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
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
    coordinates: Coordinates,
    tile_size: TileSize,
) -> list[Polygon]:
    """Generates a list of tiles from the coordinates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters

    Returns:
        list of tiles
    """
    tiles = [
        box(x_min, y_min, x_min + tile_size, y_min + tile_size)
        for x_min, y_min in coordinates
    ]
    return tiles
