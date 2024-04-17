import numpy as np
from pyproj import CRS
from pyproj.exceptions import CRSError

from src.utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
)


def raise_type_error(
    param_name: str,
    expected_type: type,
    actual_type: type,
) -> None:
    """
    | Raises a TypeError with a message indicating the expected and actual type.

    :param param_name: name of the parameter
    :param expected_type: expected type of the parameter
    :param actual_type: actual type of the parameter
    """
    message = (
        f'Invalid type for {param_name}. '
        f'Expected {expected_type}, but got {actual_type}.'
    )
    raise TypeError(message)


def validate_bounding_box(bounding_box: BoundingBox) -> None:
    """
    | Validates the bounding box.

    :param bounding_box: bounding box (x_min, y_min, x_max, y_max)
    """
    if not isinstance(bounding_box, tuple):
        raise_type_error(
            param_name='bounding_box',
            expected_type=tuple,
            actual_type=type(bounding_box),
        )

    conditions = [
        len(bounding_box) == 4,
        all(isinstance(coordinate, int) for coordinate in bounding_box),
    ]
    if not all(conditions):
        message = (
            f'Invalid values for bounding_box. '
            f'Expected a tuple of 4 integers, but got {bounding_box}.'
        )
        raise ValueError(message)

    conditions = [
        bounding_box[0] < bounding_box[2],
        bounding_box[1] < bounding_box[3],
    ]
    if not all(conditions):
        message = (
            f'Invalid values for bounding_box. '
            f'Expected (x_min, y_min, x_max, y_max) where x_min < x_max and y_min < y_max, but got {bounding_box}.'
        )
        raise ValueError(message)


def validate_coordinates(coordinates: Coordinates) -> None:
    """
    | Validates the coordinates.

    :param coordinates: coordinates (x_min, y_min) of each tile
    """
    if not isinstance(coordinates, np.ndarray):
        raise_type_error(
            param_name='coordinates',
            expected_type=np.ndarray,
            actual_type=type(coordinates),
        )

    conditions = [
        coordinates.dtype == np.int32,
        coordinates.ndim == 2,
        coordinates.shape[1] == 2,
    ]
    if not all(conditions):
        message = (
            f'Invalid array for coordinates. '
            f'Expected an array of shape (n, 2) with dtype int32, but got {coordinates}.'
        )
        raise ValueError(message)


def validate_epsg_code(epsg_code: EPSGCode) -> None:
    """
    | Validates the EPSG code.

    :param epsg_code: EPSG code
    """
    if not isinstance(epsg_code, int):
        raise_type_error(
            param_name='epsg_code',
            expected_type=int,
            actual_type=type(epsg_code),
        )

    try:
        CRS.from_epsg(epsg_code)
    except CRSError as e:
        message = (
            f'Invalid value for epsg_code. '
            f'Expected a valid EPSG code, but got {epsg_code}.'
        )
        raise ValueError(message) from e


def validate_tile_size(tile_size: TileSize) -> None:
    """
    | Validates the tile size.

    :param tile_size: tile size in meters
    """
    if not isinstance(tile_size, int):
        raise_type_error(
            param_name='tile_size',
            expected_type=int,
            actual_type=type(tile_size),
        )

    conditions = [
        tile_size > 0,
    ]
    if not all(conditions):
        message = (
            f'Invalid value for tile_size. '
            f'Expected a positive integer, but got {tile_size}.'
        )
        raise ValueError(message)
