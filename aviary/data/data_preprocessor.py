from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import pydantic
import torch

# noinspection PyProtectedMember
from aviary._functional.data.data_preprocessor import (
    composite_preprocessor,
    normalize_preprocessor,
    standardize_preprocessor,
    to_tensor_preprocessor,
)

# noinspection PyProtectedMember
from aviary._utils.mixins import FromConfigMixin


class DataPreprocessor(ABC, FromConfigMixin):
    """Abstract class for data preprocessors

    Data preprocessors are callables that preprocess data.
    The data preprocessor is used by the dataset to preprocess the fetched data for each tile.

    Currently implemented data preprocessors:
        - CompositePreprocessor: Composes multiple data preprocessors
        - NormalizePreprocessor: Applies min-max normalization
        - StandardizePreprocessor: Applies standardization
        - ToTensorPreprocessor: Converts the data to a tensor
    """

    @abstractmethod
    def __call__(
        self,
        data: npt.NDArray | torch.Tensor,
    ) -> npt.NDArray | torch.Tensor:
        """Preprocesses the data.

        Parameters:
            data: data

        Returns:
            preprocessed data
        """
        pass


class CompositePreprocessor(DataPreprocessor):
    """Data preprocessor that composes multiple data preprocessors"""

    def __init__(
        self,
        data_preprocessors: list[DataPreprocessor],
    ) -> None:
        """
        Parameters:
            data_preprocessors: data preprocessors
        """
        self.data_preprocessors = data_preprocessors

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray | torch.Tensor:
        """Preprocesses the data with each data preprocessor.

        Parameters:
            data: data

        Returns:
            preprocessed data
        """
        return composite_preprocessor(
            data=data,
            data_preprocessors=self.data_preprocessors,
        )


class CompositePreprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` classmethod of `CompositePreprocessor`

    Attributes:
        data_preprocessors: configurations of the data preprocessors
    """
    data_preprocessors: list[NormalizePreprocessorConfig | StandardizePreprocessorConfig | ToTensorPreprocessorConfig]


class NormalizePreprocessor(DataPreprocessor):
    """Data preprocessor that applies min-max normalization

    Examples:
        Assume the data is a 3-channel image of data type uint8.

        >>> min_values = [0.] * 3
        >>> max_values = [255.] * 3
        >>> normalize_preprocessor = NormalizePreprocessor(
        ...     min_values=min_values,
        ...     max_values=max_values,
        ... )
        >>> preprocessed_data = normalize_preprocessor(data)
    """

    def __init__(
        self,
        min_values: list[float],
        max_values: list[float],
    ) -> None:
        """
        Parameters:
            min_values: minimum values of the data (per channel)
            max_values: maximum values of the data (per channel)
        """
        self.min_values = min_values
        self.max_values = max_values

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray[np.float32]:
        """Preprocesses the data by applying min-max normalization.

        Parameters:
            data: data

        Returns:
            preprocessed data
        """
        return normalize_preprocessor(
            data=data,
            min_values=self.min_values,
            max_values=self.max_values,
        )


class NormalizePreprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` classmethod of `NormalizePreprocessor`

    Attributes:
        min_values: minimum values of the data (per channel)
        max_values: maximum values of the data (per channel)
    """
    min_values: list[float]
    max_values: list[float]


class StandardizePreprocessor(DataPreprocessor):
    """Data preprocessor that applies standardization

    Examples:
        Assume the data is a 3-channel image of data type float32.
        In this example the mean and standard deviation values from the ImageNet dataset are used.

        >>> mean_values = [.485, .456, .406]
        >>> std_values = [.229, .224, .225]
        >>> standardize_preprocessor = StandardizePreprocessor(
        ...     mean_values=mean_values,
        ...     std_values=std_values,
        ... )
        >>> preprocessed_data = standardize_preprocessor(data)
    """

    def __init__(
        self,
        mean_values: list[float],
        std_values: list[float],
    ) -> None:
        """
        Parameters:
            mean_values: mean values of the data (per channel)
            std_values: standard deviation values of the data (per channel)
        """
        self.mean_values = mean_values
        self.std_values = std_values

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray[np.float32]:
        """Preprocesses the data by applying standardization.

        Parameters:
            data: data

        Returns:
            preprocessed data
        """
        return standardize_preprocessor(
            data=data,
            mean_values=self.mean_values,
            std_values=self.std_values,
        )


class StandardizePreprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` classmethod of `StandardizePreprocessor`

    Attributes:
        mean_values: mean values of the data (per channel)
        std_values: standard deviation values of the data (per channel)
    """
    mean_values: list[float]
    std_values: list[float]


class ToTensorPreprocessor(DataPreprocessor):
    """Data preprocessor that converts the data to a tensor"""

    def __call__(
        self,
        data: npt.NDArray[np.float32],
    ) -> torch.Tensor:
        """Converts the data to a tensor.

        Parameters:
            data: data

        Returns:
            tensor
        """
        return to_tensor_preprocessor(
            data=data,
        )


class ToTensorPreprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` classmethod of `ToTensorPreprocessor`"""
    pass
