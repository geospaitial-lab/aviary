from unittest.mock import MagicMock

import numpy as np
import pytest

# noinspection PyProtectedMember
from aviary._functional.data.dataset import (
    get_item,
    get_length,
)

from aviary.core.type_aliases import CoordinatesSet
from aviary.data.data_fetcher import DataFetcher
from aviary.data.data_preprocessor import DataPreprocessor
from tests._functional.data.data.data_test_dataset import data_test_get_length


def test_get_item() -> None:
    data_fetcher = MagicMock(spec=DataFetcher)
    expected_data_fetcher = 'expected_data_fetcher'
    data_fetcher.return_value = expected_data_fetcher
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    index = 0
    data_preprocessor = None
    data = get_item(
        data_fetcher=data_fetcher,
        coordinates=coordinates,
        index=index,
        data_preprocessor=data_preprocessor,
    )
    data_fetcher.assert_called_once_with(
        x_min=-128,
        y_min=-128,
    )
    assert data == (expected_data_fetcher, -128, -128)

    data_fetcher = MagicMock(spec=DataFetcher)
    expected_data_fetcher = 'expected_data_fetcher'
    data_fetcher.return_value = expected_data_fetcher
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    index = 0
    data_preprocessor = MagicMock(spec=DataPreprocessor)
    expected_data_preprocessor = 'expected_data_preprocessor'
    data_preprocessor.return_value = expected_data_preprocessor
    data = get_item(
        data_fetcher=data_fetcher,
        coordinates=coordinates,
        index=index,
        data_preprocessor=data_preprocessor,
    )

    data_fetcher.assert_called_once_with(
        x_min=-128,
        y_min=-128,
    )
    data_preprocessor.assert_called_once_with(
        data=expected_data_fetcher,
    )
    assert data == (expected_data_preprocessor, -128, -128)


@pytest.mark.parametrize(('coordinates', 'expected'), data_test_get_length)
def test_get_length(
    coordinates: CoordinatesSet,
    expected: int,
) -> None:
    length = get_length(
        coordinates=coordinates,
    )

    assert length == expected
