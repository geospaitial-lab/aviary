from collections.abc import (
    Iterable,
    Iterator,
)
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from queue import Queue
from threading import Thread

from aviary.core.tiles import Tiles
from aviary.tile.tile_set import TileSet


class TileLoader(Iterable[Tiles]):
    """A tile loader is an iterable that yields tiles from the tile set.

    Example:
        Assume the tile set is already created.

        You can create a tile loader and iterate over the tiles.

        ``` python
        tile_loader = TileLoader(
            tile_set=tile_set,
            batch_size=1,
            max_num_threads=None,
            num_prefetched_tiles=1,
        )

        for tiles in tile_loader:
            ...
        ```
    """

    def __init__(
        self,
        tile_set: TileSet,
        batch_size: int = 1,
        max_num_threads: int | None = None,
        num_prefetched_tiles: int = 1,
    ) -> None:
        """
        Parameters:
            tile_set: Tile set
            batch_size: Batch size
            max_num_threads: Maximum number of threads
            num_prefetched_tiles: Number of prefetched tiles
        """
        self._tile_set = tile_set
        self._batch_size = batch_size
        self._max_num_threads = max_num_threads
        self._num_prefetched_tiles = num_prefetched_tiles

        self._index = 0
        self._prefetch_queue = Queue(self._num_prefetched_tiles)
        self._prefetch_thread = Thread(
            target=self._prefetch_tiles,
            daemon=True,
        )
        self._prefetch_thread.start()

    def _prefetch_tiles(self) -> None:
        """Prefetches tiles and puts them into the queue."""
        index = 0

        while index < len(self._tile_set):
            if self._prefetch_queue.full():
                continue

            end_index = min(index + self._batch_size, len(self._tile_set))
            indices = range(index, end_index)

            if self._max_num_threads == 1:
                tiles = [
                    self._tile_set[index]
                    for index in indices
                ]
            else:
                with ThreadPoolExecutor(max_workers=self._max_num_threads) as executor:
                    tasks = [
                        executor.submit(
                            self._tile_set.__getitem__,
                            index=index,
                        )
                        for index in indices
                    ]
                    tiles = [
                        futures.result()
                        for futures in as_completed(tasks)
                    ]

            tiles = Tiles.from_tiles(
                tiles=tiles,
                copy=False,
            )
            self._prefetch_queue.put(tiles)
            index += self._batch_size

    def __len__(self) -> int:
        """Computes the number of tiles.

        Returns:
            Number of tiles
        """
        return (len(self._tile_set) + self._batch_size - 1) // self._batch_size

    def __iter__(self) -> Iterator[Tiles]:
        """Iterates over the tiles.

        Yields:
            Tiles
        """
        self._index = 0
        return self

    def __next__(self) -> Tiles:
        """Returns the next tiles.

        Returns:
            Tiles
        """
        if self._index >= len(self._tile_set):
            raise StopIteration

        tiles = self._prefetch_queue.get()
        self._index += self._batch_size
        return tiles
