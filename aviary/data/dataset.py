import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.dataset import (
    get_item,
    get_length,
)

# noinspection PyProtectedMember
from aviary._utils.types import (
    Coordinate,
    CoordinatesSet,
)
from aviary.data.data_fetcher import DataFetcher
from aviary.data.data_preprocessor import DataPreprocessor


class Dataset:
    """A dataset is an iterable that returns a sample for each tile by calling the data fetcher and
    the data preprocessor. The dataset is used by the data loader to fetch the samples for each batch.

    Notes:
        - A sample contains the data, the minimum x coordinate and the minimum y coordinate of a tile
        - The dataset is called concurrently by the data loader

    Examples:
        Assume the data fetcher, the data preprocessor and the coordinates are already created.
        You can create a dataset and iterate over the samples.

        >>> dataset = Dataset(
        ...     data_fetcher=data_fetcher,
        ...     data_preprocessor=data_preprocessor,
        ...     coordinates=coordinates,
        ... )
        ...
        >>> for data, x_min, y_min in dataset:
        ...     ...
    """

    def __init__(
        self,
        data_fetcher: DataFetcher,
        data_preprocessor: DataPreprocessor,
        coordinates: CoordinatesSet,
    ) -> None:
        """
        Parameters:
            data_fetcher: data fetcher
            data_preprocessor: data preprocessor
            coordinates: coordinates (x_min, y_min) of each tile
        """
        self.data_fetcher = data_fetcher
        self.data_preprocessor = data_preprocessor
        self.coordinates = coordinates

    def __len__(self) -> int:
        """Computes the number of samples.

        Returns:
            number of samples
        """
        return get_length(
            coordinates=self.coordinates,
        )

    def __getitem__(
        self,
        index: int,
    ) -> tuple[npt.NDArray, Coordinate, Coordinate]:
        """Returns the sample.

        Parameters:
            index: index of the tile

        Returns:
            sample
        """
        return get_item(
            coordinates=self.coordinates,
            index=index,
            data_fetcher=self.data_fetcher,
            data_preprocessor=self.data_preprocessor,
        )
