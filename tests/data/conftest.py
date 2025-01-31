from unittest.mock import MagicMock

import pytest

from aviary.data.data_preprocessor import (
    CompositePreprocessor,
    DataPreprocessor,
    NormalizePreprocessor,
    StandardizePreprocessor,
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
