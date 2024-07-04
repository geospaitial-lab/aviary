from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# noinspection PyProtectedMember
from aviary._utils.types import InterpolationMode
from aviary.data.data_fetcher import (
    DataFetcher,
    VRTDataFetcher,
)
from aviary.data.data_preprocessor import (
    CompositePreprocessor,
    DataPreprocessor,
    NormalizePreprocessor,
    StandardizePreprocessor,
)
from aviary.data.dataset import Dataset


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
    data_fetcher = MagicMock(spec=DataFetcher)
    data_preprocessor = MagicMock(spec=DataPreprocessor)
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    return Dataset(
        data_fetcher=data_fetcher,
        data_preprocessor=data_preprocessor,
        coordinates=coordinates,
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


@pytest.fixture(scope='session')
@patch('aviary.data.data_fetcher.vrt_data_fetcher_info')
def vrt_data_fetcher(
    _mocked_vrt_data_fetcher_info,
) -> VRTDataFetcher:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    return VRTDataFetcher(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )
