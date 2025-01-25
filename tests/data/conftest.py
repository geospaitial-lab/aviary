from unittest.mock import MagicMock

import numpy as np
import pytest

from aviary.data.data_preprocessor import (
    CompositePreprocessor,
    DataPreprocessor,
    NormalizePreprocessor,
    StandardizePreprocessor,
)
from aviary.data.dataset import Dataset
from aviary.inference.tile_fetcher import TileFetcher


@pytest.fixture(scope='session')
def composite_preprocessor() -> CompositePreprocessor:
    data_preprocessors = [
        MagicMock(spec=DataPreprocessor),
        MagicMock(spec=DataPreprocessor),
        MagicMock(spec=DataPreprocessor),
    ]
    return CompositePreprocessor(
        data_preprocessors=data_preprocessors,
    )


@pytest.fixture(scope='session')
def dataset() -> Dataset:
    data_fetcher = MagicMock(spec=TileFetcher)
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    data_preprocessor = None
    return Dataset(
        data_fetcher=data_fetcher,
        coordinates=coordinates,
        data_preprocessor=data_preprocessor,
    )


@pytest.fixture(scope='session')
def normalize_preprocessor() -> NormalizePreprocessor:
    min_values = [0.] * 3
    max_values = [255.] * 3
    return NormalizePreprocessor(
        min_values=min_values,
        max_values=max_values,
    )


@pytest.fixture(scope='session')
def standardize_preprocessor() -> StandardizePreprocessor:
    mean_values = [0.] * 3
    std_values = [1.] * 3
    return StandardizePreprocessor(
        mean_values=mean_values,
        std_values=std_values,
    )
