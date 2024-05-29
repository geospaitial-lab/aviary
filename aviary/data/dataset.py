import torch.utils.data

from ..data import (
    DataFetcher,
    DataPreprocessor,
)
from .._functional.data.dataset import (
    get_item,
    get_length,
)
from .._utils.types import (
    Coordinates,
    XMin,
    YMin,
)


class Dataset(torch.utils.data.Dataset):
    """Dataset

    A dataset is an iterable that returns data for each tile by calling the data fetcher and data preprocessor.
    The dataset is used by the dataloader to fetch and preprocess data for each batch.
    """

    def __init__(
        self,
        data_fetcher: DataFetcher,
        data_preprocessor: DataPreprocessor,
        coordinates: Coordinates,
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
        """Computes the number of tiles.

        Returns:
            number of tiles
        """
        return get_length(
            coordinates=self.coordinates,
        )

    def __getitem__(
        self,
        index: int,
    ) -> tuple[torch.Tensor, XMin, YMin]:
        """Fetches and preprocesses data given the index of the tile.

        Parameters:
            index: index of the tile

        Returns:
            data and coordinates (x_min, y_min) of the tile
        """
        return get_item(
            coordinates=self.coordinates,
            index=index,
            data_fetcher=self.data_fetcher,
            data_preprocessor=self.data_preprocessor,
        )
