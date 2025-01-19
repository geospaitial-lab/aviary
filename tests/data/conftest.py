from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from aviary.core.enums import (
    InterpolationMode,
    WMSVersion,
)
from aviary.data.data_fetcher import (
    CompositeFetcher,
    DataFetcher,
    VRTFetcher,
    WMSFetcher,
)
from aviary.data.data_preprocessor import (
    CompositePreprocessor,
    DataPreprocessor,
    NormalizePreprocessor,
    StandardizePreprocessor,
)
from aviary.data.dataset import Dataset


@pytest.fixture(scope='session')
def composite_fetcher() -> CompositeFetcher:
    data_fetchers = [
        MagicMock(spec=DataFetcher),
        MagicMock(spec=DataFetcher),
        MagicMock(spec=DataFetcher),
    ]
    num_workers = 1
    return CompositeFetcher(
        data_fetchers=data_fetchers,
        num_workers=num_workers,
    )


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


@pytest.fixture(scope='session')
def vrt_fetcher() -> VRTFetcher:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    return VRTFetcher(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )


@pytest.fixture(scope='session')
def wms_fetcher() -> WMSFetcher:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    drop_channels = None
    return WMSFetcher(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )
