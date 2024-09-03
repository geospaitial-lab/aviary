from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from aviary._utils.types import (
        Coordinate,
        CoordinatesSet,
    )
    from aviary.data.data_fetcher import DataFetcher
    from aviary.data.data_preprocessor import DataPreprocessor


def get_item(
    data_fetcher: DataFetcher,
    coordinates: CoordinatesSet,
    index: int,
    data_preprocessor: DataPreprocessor | None = None,
) -> tuple[npt.NDArray, Coordinate, Coordinate]:
    """Returns the sample.

    Parameters:
        data_fetcher: data fetcher
        coordinates: coordinates (x_min, y_min) of each tile
        index: index of the tile
        data_preprocessor: data preprocessor

    Returns:
        sample
    """
    x_min, y_min = coordinates[index]
    data = data_fetcher(
        x_min=x_min,
        y_min=y_min,
    )

    if data_preprocessor is not None:
        data = data_preprocessor(
            data=data,
        )

    return data, x_min, y_min


def get_length(
    coordinates: CoordinatesSet,
) -> int:
    """Computes the number of samples.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile

    Returns:
        number of samples
    """
    return len(coordinates)
