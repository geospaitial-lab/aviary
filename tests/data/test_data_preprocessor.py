from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import aviary.data.data_preprocessor
from aviary.data.data_preprocessor import (
    CompositePreprocessor,
    DataPreprocessor,
    NormalizePreprocessor,
    NormalizePreprocessorConfig,
    StandardizePreprocessor,
    StandardizePreprocessorConfig,
)


def test_globals() -> None:
    class_names = [
        'NormalizePreprocessor',
        'StandardizePreprocessor',
    ]

    for class_name in class_names:
        assert hasattr(aviary.data.data_preprocessor, class_name)


def test_composite_preprocessor_init() -> None:
    data_preprocessors = [
        MagicMock(spec=DataPreprocessor),
        MagicMock(spec=DataPreprocessor),
        MagicMock(spec=DataPreprocessor),
    ]
    composite_preprocessor = CompositePreprocessor(
        data_preprocessors=data_preprocessors,
    )

    assert composite_preprocessor.data_preprocessors == data_preprocessors


@pytest.mark.skip(reason='Not implemented')
def test_composite_preprocessor_from_config() -> None:
    pass


@patch('aviary.data.data_preprocessor.composite_preprocessor')
def test_composite_preprocessor_call(
    mocked_composite_preprocessor: MagicMock,
    composite_preprocessor: CompositePreprocessor,
) -> None:
    data = np.array(
        [
            [[0, 127, 255], [255, 0, 127]],
            [[127, 255, 0], [0, 127, 255]],
        ],
        dtype=np.uint8,
    )
    expected = 'expected'
    mocked_composite_preprocessor.return_value = expected
    preprocessed_data = composite_preprocessor(
        data=data,
    )

    mocked_composite_preprocessor.assert_called_once_with(
        data=data,
        data_preprocessors=composite_preprocessor.data_preprocessors,
    )
    assert preprocessed_data == expected


def test_normalize_preprocessor_init() -> None:
    min_values = [0.] * 3
    max_values = [255.] * 3
    normalize_preprocessor = NormalizePreprocessor(
        min_values=min_values,
        max_values=max_values,
    )

    assert normalize_preprocessor.min_values == min_values
    assert normalize_preprocessor.max_values == max_values


def test_normalize_preprocessor_from_config() -> None:
    min_values = [0.] * 3
    max_values = [255.] * 3
    normalize_preprocessor_config = NormalizePreprocessorConfig(
        min_values=min_values,
        max_values=max_values,
    )
    normalize_preprocessor = NormalizePreprocessor.from_config(normalize_preprocessor_config)

    assert normalize_preprocessor.min_values == min_values
    assert normalize_preprocessor.max_values == max_values


@patch('aviary.data.data_preprocessor.normalize_preprocessor')
def test_normalize_preprocessor_call(
    mocked_normalize_preprocessor: MagicMock,
    normalize_preprocessor: NormalizePreprocessor,
) -> None:
    data = np.array(
        [
            [[0, 127, 255], [255, 0, 127]],
            [[127, 255, 0], [0, 127, 255]],
        ],
        dtype=np.uint8,
    )
    expected = 'expected'
    mocked_normalize_preprocessor.return_value = expected
    preprocessed_data = normalize_preprocessor(
        data=data,
    )

    mocked_normalize_preprocessor.assert_called_once_with(
        data=data,
        min_values=normalize_preprocessor.min_values,
        max_values=normalize_preprocessor.max_values,
    )
    assert preprocessed_data == expected


def test_standardize_preprocessor_init() -> None:
    mean_values = [0.] * 3
    std_values = [1.] * 3
    standardize_preprocessor = StandardizePreprocessor(
        mean_values=mean_values,
        std_values=std_values,
    )

    assert standardize_preprocessor.mean_values == mean_values
    assert standardize_preprocessor.std_values == std_values


def test_standardize_preprocessor_from_config() -> None:
    mean_values = [0.] * 3
    std_values = [1.] * 3
    standardize_preprocessor_config = StandardizePreprocessorConfig(
        mean_values=mean_values,
        std_values=std_values,
    )
    standardize_preprocessor = StandardizePreprocessor.from_config(standardize_preprocessor_config)

    assert standardize_preprocessor.mean_values == mean_values
    assert standardize_preprocessor.std_values == std_values


@patch('aviary.data.data_preprocessor.standardize_preprocessor')
def test_standardize_preprocessor_call(
    mocked_standardize_preprocessor: MagicMock,
    standardize_preprocessor: StandardizePreprocessor,
) -> None:
    data = np.array(
        [
            [[0, .5, 1], [1, 0, .5]],
            [[.5, 1, 0], [0, .5, 1]],
        ],
        dtype=np.float32,
    )
    expected = 'expected'
    mocked_standardize_preprocessor.return_value = expected
    preprocessed_data = standardize_preprocessor(
        data=data,
    )

    mocked_standardize_preprocessor.assert_called_once_with(
        data=data,
        mean_values=standardize_preprocessor.mean_values,
        std_values=standardize_preprocessor.std_values,
    )
    assert preprocessed_data == expected
