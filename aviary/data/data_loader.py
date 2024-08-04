from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.data_loader import collate_batch

# noinspection PyProtectedMember
from aviary._utils.types import Coordinate

if TYPE_CHECKING:
    from aviary.data.dataset import Dataset


class DataLoader(Iterator[tuple[npt.NDArray, Coordinate, Coordinate]]):
    """A data loader is an iterator that yields batches from the dataset.
    The data loader is used by the pipeline to fetch the batches for inference.

    Notes:
        - A batch contains the data, the minimum x coordinates and the minimum y coordinates of a batch of tiles
        - The data loader uses multiple threads to fetch the samples from the dataset
        - The data loader can prefetch multiple batches

    Examples:
        Assume the dataset is already created.

        You can create a data loader and iterate over the batches.

        >>> data_loader = DataLoader(
        ...     dataset=dataset,
        ...     batch_size=1,
        ...     num_workers=4,
        ...     num_prefetched_batches=1,
        ... )
        ...
        >>> for data, x_min, y_min in data_loader:
        ...     ...
    """

    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 1,
        num_workers: int = 4,
        num_prefetched_batches: int = 1,
    ) -> None:
        """
        Parameters:
            dataset: dataset
            batch_size: batch size
            num_workers: number of workers
            num_prefetched_batches: number of prefetched batches
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.num_prefetched_batches = num_prefetched_batches

        self._index = 0
        self._prefetch_queue = Queue(self.num_prefetched_batches)
        self._prefetch_thread = Thread(
            target=self._prefetch_batches,
            daemon=True,
        )
        self._prefetch_thread.start()

    def __len__(self) -> int:
        """Computes the number of batches.

        Returns:
            number of batches
        """
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size

    def __iter__(self) -> DataLoader:
        """Initializes the data loader.

        Returns:
            data loader
        """
        self._index = 0
        return self

    def __next__(self) -> tuple[npt.NDArray, Coordinate, Coordinate]:
        """Returns the next batch.

        Returns:
            batch

        Raises:
            StopIteration
        """
        if self._index >= len(self.dataset):
            raise StopIteration

        batch = self._prefetch_queue.get()
        self._index += self.batch_size
        return batch

    def _prefetch_batches(self) -> None:
        """Prefetches batches from the dataset and puts them into the `_prefetch_queue` queue.

        Notes:
            - This method is called by the `_prefetch_thread` thread
        """
        index = 0
        while index < len(self.dataset):
            if self._prefetch_queue.full():
                continue

            end_index = min(index + self.batch_size, len(self.dataset))
            sample_indices = range(index, end_index)

            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                tasks = [
                    executor.submit(
                        self.dataset.__getitem__,
                        index=sample_index,
                    )
                    for sample_index in sample_indices
                ]
                samples = [
                    futures.result()
                    for futures in as_completed(tasks)
                ]

            batch = collate_batch(samples)
            self._prefetch_queue.put(batch)
            index += self.batch_size
