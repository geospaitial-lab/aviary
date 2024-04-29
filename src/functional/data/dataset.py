from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from src.data.data_fetcher import DataFetcher
    from src.data.data_preprocessor import DataPreprocessor
from src.utils.types import (
    Coordinates,
)


def get_item(
    coordinates: Coordinates,
    index: int,
    data_fetcher: DataFetcher,
    data_preprocessor: DataPreprocessor,
) -> torch.Tensor:
    """
    | Returns the data.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param index: index of the tile
    :param data_fetcher: data fetcher
    :param data_preprocessor: data preprocessor
    :return: data
    """
    x_min, y_min = coordinates[index]
    data = data_fetcher(
        x_min=x_min,
        y_min=y_min,
    )
    data = data_preprocessor(
        data=data,
    )
    return data


def get_length(
    coordinates: Coordinates,
) -> int:
    """
    | Returns the number of tiles.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :return: number of tiles
    """
    return len(coordinates)
