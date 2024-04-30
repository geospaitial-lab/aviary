import torch.utils.data

from src.data.data_fetcher import DataFetcher
from src.data.data_preprocessor import DataPreprocessor
from src.functional.data.dataset import (
    get_item,
    get_length,
)
from src.utils.types import (
    Coordinates,
)


class Dataset(torch.utils.data.Dataset):

    def __init__(
        self,
        data_fetcher: DataFetcher,
        data_preprocessor: DataPreprocessor,
        coordinates: Coordinates,
    ) -> None:
        """
        :param data_fetcher: data fetcher
        :param data_preprocessor: data preprocessor
        :param coordinates: coordinates (x_min, y_min) of each tile
        """
        self.data_fetcher = data_fetcher
        self.data_preprocessor = data_preprocessor
        self.coordinates = coordinates

    def __len__(self) -> int:
        """
        | Returns the number of tiles.

        :return: number of tiles
        """
        return get_length(
            coordinates=self.coordinates,
        )

    def __getitem__(
        self,
        index: int,
    ) -> torch.Tensor:
        """
        | Returns the data.

        :param index: index of the tile
        :return: data
        """
        return get_item(
            coordinates=self.coordinates,
            index=index,
            data_fetcher=self.data_fetcher,
            data_preprocessor=self.data_preprocessor,
        )
