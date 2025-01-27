from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aviary.core.process_area import ProcessArea
    from aviary.core.tile import Tile
    from aviary.inference.tile_fetcher import TileFetcher


def get_item(
    process_area: ProcessArea,
    index: int,
    tile_fetcher: TileFetcher,
) -> Tile:
    """Returns the tile.

    Parameters:
        process_area: process area
        index: index of the tile
        tile_fetcher: tile fetcher

    Returns:
        tile
    """
    coordinates = process_area[index]
    return tile_fetcher(coordinates=coordinates)


def get_length(
    process_area: ProcessArea,
) -> int:
    """Computes the number of tiles.

    Parameters:
        process_area: process area

    Returns:
        number of tiles
    """
    return len(process_area)
