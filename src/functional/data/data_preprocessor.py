from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
import torch

if TYPE_CHECKING:
    from src.data.data_preprocessor import DataPreprocessor


def composite_preprocessor(
    data: npt.NDArray,
    data_preprocessors: list[DataPreprocessor],
) -> npt.NDArray | torch.Tensor:
    """
    | Preprocesses the data with each data preprocessor.

    :param data: data
    :param data_preprocessors: data preprocessors
    :return: preprocessed data
    """
    for data_preprocessor in data_preprocessors:
        data = data_preprocessor(data)
    return data


def normalize_preprocessor(
    data: npt.NDArray,
    min_values: list[float],
    max_values: list[float],
) -> npt.NDArray[np.float32]:
    """
    | Preprocesses the data by applying min-max normalization.

    :param data: data
    :param min_values: minimum values of the data (per channel)
    :param max_values: maximum values of the data (per channel)
    :return: preprocessed data
    """
    min_values = np.array(min_values, dtype=np.float32)
    max_values = np.array(max_values, dtype=np.float32)
    return (data - min_values) / (max_values - min_values)


def standardize_preprocessor(
    data: npt.NDArray,
    mean_values: list[float],
    std_values: list[float],
) -> npt.NDArray[np.float32]:
    """
    | Preprocesses the data by applying standardization.

    :param data: data
    :param mean_values: mean values of the data (per channel)
    :param std_values: standard deviation values of the data (per channel)
    :return: preprocessed data
    """
    mean_values = np.array(mean_values, dtype=np.float32)
    std_values = np.array(std_values, dtype=np.float32)
    return (data - mean_values) / std_values


def to_tensor_preprocessor(
    data: npt.NDArray[np.float32],
) -> torch.Tensor:
    """
    | Converts the data to a tensor.

    :param data: data
    :return: tensor
    """
    return torch.from_numpy(data).permute(2, 0, 1)