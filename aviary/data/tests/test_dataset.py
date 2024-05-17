from unittest.mock import MagicMock, patch

import numpy as np

from ...data import (
    DataFetcher,
    DataPreprocessor,
    Dataset,
)


def test_init() -> None:
    data_fetcher = MagicMock(spec=DataFetcher)
    data_preprocessor = MagicMock(spec=DataPreprocessor)
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    dataset = Dataset(
        data_fetcher=data_fetcher,
        data_preprocessor=data_preprocessor,
        coordinates=coordinates,
    )

    assert dataset.data_fetcher == data_fetcher
    assert dataset.data_preprocessor == data_preprocessor
    np.testing.assert_array_equal(dataset.coordinates, coordinates)


@patch('aviary.data.dataset.get_item')
def test_getitem(
    mocked_get_item,
    dataset: Dataset,
) -> None:
    index = 0
    expected = 'expected'
    mocked_get_item.return_value = expected
    item = dataset[index]

    mocked_get_item.assert_called_once_with(
        coordinates=dataset.coordinates,
        index=index,
        data_fetcher=dataset.data_fetcher,
        data_preprocessor=dataset.data_preprocessor,
    )
    assert item == expected


@patch('aviary.data.dataset.get_length')
def test_len(
    mocked_get_length,
    dataset: Dataset,
) -> None:
    expected = 1
    mocked_get_length.return_value = expected
    length = len(dataset)

    mocked_get_length.assert_called_once_with(
        coordinates=dataset.coordinates,
    )
    assert length == expected
