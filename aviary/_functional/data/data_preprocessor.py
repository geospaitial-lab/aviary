from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from aviary.data.data_preprocessor import DataPreprocessor


def composite_preprocessor(
    data: npt.NDArray,
    data_preprocessors: list[DataPreprocessor],
) -> npt.NDArray:
    """Preprocesses the data with each data preprocessor.

    Parameters:
        data: data
        data_preprocessors: data preprocessors

    Returns:
        preprocessed data
    """
    for data_preprocessor in data_preprocessors:
        data = data_preprocessor(data)

    return data


def normalize_preprocessor(
    data: npt.NDArray,
    min_values: list[float],
    max_values: list[float],
) -> npt.NDArray[np.float32]:
    """Preprocesses the data by applying min-max normalization.

    Parameters:
        data: data
        min_values: minimum values of the data (per channel)
        max_values: maximum values of the data (per channel)

    Returns:
        preprocessed data
    """
    min_values = np.array(min_values, dtype=np.float32)
    max_values = np.array(max_values, dtype=np.float32)
    return (data - min_values) / (max_values - min_values)


def standardize_preprocessor(
    data: npt.NDArray,
    mean_values: list[float],
    std_values: list[float],
) -> npt.NDArray[np.float32]:
    """Preprocesses the data by applying standardization.

    Parameters:
        data: data
        mean_values: mean values of the data (per channel)
        std_values: standard deviation values of the data (per channel)

    Returns:
        preprocessed data
    """
    mean_values = np.array(mean_values, dtype=np.float32)
    std_values = np.array(std_values, dtype=np.float32)
    return (data - mean_values) / std_values
