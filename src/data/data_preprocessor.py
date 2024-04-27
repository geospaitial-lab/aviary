from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import torch

from src.functional.data.data_preprocessor import (
    composite_preprocessor,
    normalize_preprocessor,
    standardize_preprocessor,
    to_tensor_preprocessor,
)


class DataPreprocessor(ABC):

    @abstractmethod
    def __call__(
        self,
        data: npt.NDArray | torch.Tensor,
    ) -> npt.NDArray | torch.Tensor:
        """
        | Preprocesses the data.

        :param data: data
        :return: preprocessed data
        """
        pass


class CompositePreprocessor(DataPreprocessor):

    def __init__(
        self,
        data_preprocessors: list[DataPreprocessor],
    ) -> None:
        """
        :param data_preprocessors: data preprocessors
        """
        self.data_preprocessors = data_preprocessors

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray | torch.Tensor:
        """
        | Preprocesses the data with each data preprocessor.

        :param data: data
        :return: preprocessed data
        """
        return composite_preprocessor(
            data=data,
            data_preprocessors=self.data_preprocessors,
        )


class NormalizePreprocessor(DataPreprocessor):

    def __init__(
        self,
        min_values: list[float],
        max_values: list[float],
    ) -> None:
        """
        :param min_values: minimum values of the data (per channel)
        :param max_values: maximum values of the data (per channel)
        """
        self.min_values = min_values
        self.max_values = max_values

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray[np.float32]:
        """
        | Preprocesses the data by applying min-max normalization.

        :param data: data
        :return: preprocessed data
        """
        return normalize_preprocessor(
            data=data,
            min_values=self.min_values,
            max_values=self.max_values,
        )


class StandardizePreprocessor(DataPreprocessor):

    def __init__(
        self,
        mean_values: list[float],
        std_values: list[float],
    ) -> None:
        """
        :param mean_values: mean values of the data (per channel)
        :param std_values: standard deviation values of the data (per channel)
        """
        self.mean_values = mean_values
        self.std_values = std_values

    def __call__(
        self,
        data: npt.NDArray[np.float32],
    ) -> npt.NDArray[np.float32]:
        """
        | Preprocesses the data by applying standardization.

        :param data: data
        :return: preprocessed data
        """
        return standardize_preprocessor(
            data=data,
            mean_values=self.mean_values,
            std_values=self.std_values,
        )


class ToTensorPreprocessor(DataPreprocessor):

    def __call__(
        self,
        data: npt.NDArray[np.float32],
    ) -> torch.Tensor:
        """
        | Converts the data to a tensor.

        :param data: data
        :return: tensor
        """
        return to_tensor_preprocessor(
            data=data,
        )
