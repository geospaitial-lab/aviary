from collections.abc import (
    Iterable,
    Iterator,
)

from aviary.core.grid import Grid
from aviary.core.tiles import Tile
from aviary.tile.tile_fetcher import TileFetcher


class TileSet(Iterable[Tile]):
    """A tile set is an iterable that yields a tile for each coordinates in the grid by calling the tile fetcher.

    Example:
        Assume the grid and the tile fetcher are already created.

        You can create a tile set and iterate over the tiles.

        ``` python
        tile_set = TileSet(
            grid=grid,
            tile_fetcher=tile_fetcher,
        )

        for tile in tile_set:
            ...
        ```
    """

    def __init__(
        self,
        grid: Grid,
        tile_fetcher: TileFetcher,
    ) -> None:
        """
        Parameters:
            grid: Grid
            tile_fetcher: Tile fetcher
        """
        self._grid = grid
        self._tile_fetcher = tile_fetcher

    def __len__(self) -> int:
        """Computes the number of tiles.

        Returns:
            Number of tiles
        """
        return len(self._grid)

    def __getitem__(
        self,
        index: int,
    ) -> Tile:
        """Returns the tile.

        Parameters:
            index: Index of the tile

        Returns:
            Tile
        """
        coordinates = self._grid[index]
        return self._tile_fetcher(coordinates=coordinates)

    def __iter__(self) -> Iterator[Tile]:
        """Iterates over the tiles.

        Yields:
            Tile
        """
        for index in range(len(self)):
            yield self[index]
