from aviary.core.process_area import ProcessArea
from aviary.core.tiles import Tile
from aviary.inference.tile_fetcher import TileFetcher


class TileSet:
    """A tile set is an iterable that returns a tile for each coordinates in the process area
    by calling the tile fetcher.
    The tile set is used by the tile loader to fetch the tiles for each batch.

    Examples:
        Assume the process area and the tile fetcher are already created.

        You can create a tile set and iterate over the tiles.

        >>> tile_set = TileSet(
        ...     process_area=process_area,
        ...     tile_fetcher=tile_fetcher,
        ... )
        ...
        >>> for tile in tile_set:
        ...     ...
    """

    def __init__(
        self,
        process_area: ProcessArea,
        tile_fetcher: TileFetcher,
    ) -> None:
        """
        Parameters:
            process_area: Process area
            tile_fetcher: Tile fetcher
        """
        self._process_area = process_area
        self._tile_fetcher = tile_fetcher

    def __len__(self) -> int:
        """Computes the number of tiles.

        Returns:
            Number of tiles
        """
        return len(self._process_area)

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
        coordinates = self._process_area[index]
        return self._tile_fetcher(coordinates=coordinates)
