import numpy as np
import numpy.typing as npt
import pytest

# noinspection PyProtectedMember
from aviary._functional.data.data_preprocessor import (
    normalize_preprocessor,
    standardize_preprocessor,
)
from tests._functional.data.data.data_test_data_preprocessor import (
    data_test_normalize_preprocessor,
    data_test_standardize_preprocessor,
)


@pytest.mark.skip(reason='Not implemented')
def test_composite_preprocessor() -> None:
    pass


@pytest.mark.parametrize(('data', 'min_values', 'max_values', 'expected'), data_test_normalize_preprocessor)
def test_normalize_preprocessor(
    data: npt.NDArray,
    min_values: list[float],
    max_values: list[float],
    expected: npt.NDArray[np.float32],
) -> None:
    preprocessed_data = normalize_preprocessor(
        data=data,
        min_values=min_values,
        max_values=max_values,
    )

    np.testing.assert_array_equal(preprocessed_data, expected)


@pytest.mark.parametrize(('data', 'mean_values', 'std_values', 'expected'), data_test_standardize_preprocessor)
def test_standardize_preprocessor(
    data: npt.NDArray,
    mean_values: list[float],
    std_values: list[float],
    expected: npt.NDArray[np.float32],
) -> None:
    preprocessed_data = standardize_preprocessor(
        data=data,
        mean_values=mean_values,
        std_values=std_values,
    )

    np.testing.assert_array_equal(preprocessed_data, expected)
