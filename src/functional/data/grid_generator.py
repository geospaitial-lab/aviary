import geopandas as gpd
import numpy as np
from shapely.geometry import box, Polygon

from src.utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
    XMax,
    XMin,
    YMax,
    YMin,
)
from src.utils.validators import (
    raise_type_error,
    validate_bounding_box,
    validate_epsg_code,
    validate_tile_size,
)


def compute_coordinates(
    tile_size: TileSize,
    x_min: XMin,
    y_min: YMin,
    x_max: XMax,
    y_max: YMax,
    quantize: bool = True,
) -> Coordinates:
    """
    | Computes the coordinates of the bottom left corner of each tile.

    :param tile_size: tile size in meters
    :param x_min: minimum x coordinate of the bounding box
    :param y_min: minimum y coordinate of the bounding box
    :param x_max: maximum x coordinate of the bounding box
    :param y_max: maximum y coordinate of the bounding box
    :param quantize: if True, the bounding box is quantized to tile_size
    :return: coordinates (x_min, y_min) of each tile
    """
    _validate_compute_coordinates(
        tile_size=tile_size,
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
        quantize=quantize,
    )

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


def generate_grid(
    tile_size: TileSize,
    x_min: XMin,
    y_min: YMin,
    x_max: XMax,
    y_max: YMax,
    epsg_code: EPSGCode,
    quantize: bool = True,
) -> gpd.GeoDataFrame:
    """
    | Generates a geodataframe of the grid.

    :param tile_size: tile size in meters
    :param x_min: minimum x coordinate of the bounding box
    :param y_min: minimum y coordinate of the bounding box
    :param x_max: maximum x coordinate of the bounding box
    :param y_max: maximum y coordinate of the bounding box
    :param epsg_code: EPSG code
    :param quantize: if True, the bounding box is quantized to tile_size
    :return: grid
    """
    _validate_generate_grid(
        tile_size=tile_size,
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
        epsg_code=epsg_code,
        quantize=quantize,
    )

    coordinates = compute_coordinates(
        tile_size=tile_size,
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
        quantize=quantize,
    )
    polygons = _generate_polygons(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    return gpd.GeoDataFrame(
        geometry=polygons,
        crs=f'EPSG:{epsg_code}',
    )


def _generate_polygons(
    coordinates: Coordinates,
    tile_size: TileSize,
) -> list[Polygon]:
    """
    | Generates a list of polygons from the coordinates.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param tile_size: tile size in meters
    :return: list of polygons
    """
    polygons = [
        box(x_min, y_min, x_min + tile_size, y_min + tile_size)
        for x_min, y_min in coordinates
    ]
    return polygons


def _quantize_coordinates(
    x_min: XMin,
    y_min: YMin,
    tile_size: TileSize,
) -> tuple[XMin, YMin]:
    """
    | Quantizes the coordinates of the bottom left corner of the bounding box to the tile size.

    :param x_min: minimum x coordinate
    :param y_min: minimum y coordinate
    :param tile_size: tile size in meters
    :return: quantized coordinates (x_min, y_min) of the bounding box
    """
    x_min = x_min - (x_min % tile_size)
    y_min = y_min - (y_min % tile_size)
    return x_min, y_min


def _validate_compute_coordinates(
    tile_size: TileSize,
    x_min: XMin,
    y_min: YMin,
    x_max: XMax,
    y_max: YMax,
    quantize: bool,
) -> None:
    """
    | Validates the input parameters of compute_coordinates.

    :param tile_size: tile size in meters
    :param x_min: minimum x coordinate of the bounding box
    :param y_min: minimum y coordinate of the bounding box
    :param x_max: maximum x coordinate of the bounding box
    :param y_max: maximum y coordinate of the bounding box
    :param quantize: if True, the bounding box is quantized to tile_size
    """
    validate_tile_size(tile_size)
    validate_bounding_box((x_min, y_min, x_max, y_max))
    _validate_quantize(quantize)


def _validate_generate_grid(
    tile_size: TileSize,
    x_min: XMin,
    y_min: YMin,
    x_max: XMax,
    y_max: YMax,
    epsg_code: EPSGCode,
    quantize: bool,
) -> None:
    """
    | Validates the input parameters of generate_grid.

    :param tile_size: tile size in meters
    :param x_min: minimum x coordinate of the bounding box
    :param y_min: minimum y coordinate of the bounding box
    :param x_max: maximum x coordinate of the bounding box
    :param y_max: maximum y coordinate of the bounding box
    :param epsg_code: EPSG code
    :param quantize: if True, the bounding box is quantized to tile_size
    """
    validate_tile_size(tile_size)
    validate_bounding_box((x_min, y_min, x_max, y_max))
    validate_epsg_code(epsg_code)
    _validate_quantize(quantize)


def validate_grid_generator(
    bounding_box: BoundingBox,
    epsg_code: EPSGCode,
) -> None:
    """
    | Validates the input parameters of GridGenerator.

    :param bounding_box: bounding box (x_min, y_min, x_max, y_max)
    :param epsg_code: EPSG code
    """
    validate_bounding_box(bounding_box)
    validate_epsg_code(epsg_code)


def _validate_quantize(quantize: bool) -> None:
    """
    | Validates the quantize parameter.

    :param quantize: if True, the bounding box is quantized to tile_size
    """
    if not isinstance(quantize, bool):
        raise_type_error(
            param_name='quantize',
            expected_type=bool,
            actual_type=type(quantize),
        )
