from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from ...data import (
        DataFetcher,
        DataPreprocessor,
    )
from ..._utils.types import (
    Coordinate,
    Coordinates,
)


def get_item(
    data_fetcher: DataFetcher,
    data_preprocessor: DataPreprocessor,
    coordinates: Coordinates,
    index: int,
) -> tuple[torch.Tensor, Coordinate, Coordinate]:
    """Fetches and preprocesses data given the index of the tile.

    Parameters:
        data_fetcher: data fetcher
        data_preprocessor: data preprocessor
        coordinates: coordinates (x_min, y_min) of each tile
        index: index of the tile

    Returns:
        data and coordinates (x_min, y_min) of the tile
    """
    x_min, y_min = coordinates[index]
    data = data_fetcher(
        x_min=x_min,
        y_min=y_min,
    )
    data = data_preprocessor(
        data=data,
    )
    return data, x_min, y_min


def get_length(
    coordinates: Coordinates,
) -> int:
    """Computes the number of tiles.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile

    Returns:
        number of tiles
    """
    return len(coordinates)
