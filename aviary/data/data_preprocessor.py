from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pydantic

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.data.data_preprocessor import (
    composite_preprocessor,
    normalize_preprocessor,
    standardize_preprocessor,
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
    """

    @abstractmethod
    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray:
        """Preprocesses the data.

        Parameters:
            data: data

        Returns:
            preprocessed data
        """


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

    @classmethod
    def from_config(
        cls,
        config: CompositePreprocessorConfig,
    ) -> CompositePreprocessor:
        """Creates a composite preprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            composite preprocessor
        """
        data_preprocessors = []

        for data_preprocessor_config in config.data_preprocessors_configs:
            data_preprocessor_class = globals()[data_preprocessor_config.name]
            data_preprocessor = data_preprocessor_class.from_config(data_preprocessor_config.config)
            data_preprocessors.append(data_preprocessor)

        return cls(
            data_preprocessors=data_preprocessors,
        )

    def __call__(
        self,
        data: npt.NDArray,
    ) -> npt.NDArray:
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
    """Configuration for the `from_config` class method of `CompositePreprocessor`

    Attributes:
        data_preprocessors_configs: configurations of the data preprocessors
    """
    data_preprocessors_configs: list[DataPreprocessorConfig]


class DataPreprocessorConfig(pydantic.BaseModel):
    """Configuration for data preprocessors

    Attributes:
        name: name of the data preprocessor
        config: configuration of the data preprocessor
    """
    name: str
    config: NormalizePreprocessorConfig | StandardizePreprocessorConfig


class NormalizePreprocessor(DataPreprocessor):
    """Data preprocessor that applies min-max normalization

    Examples:
        Assume the data is a 3-channel image of data type uint8.

        >>> normalize_preprocessor = NormalizePreprocessor(
        ...     min_values=[0.] * 3,
        ...     max_values=[255.] * 3,
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

    @classmethod
    def from_config(
        cls,
        config: NormalizePreprocessorConfig,
    ) -> NormalizePreprocessor:
        """Creates a normalize preprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            normalize preprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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
    """Configuration for the `from_config` class method of `NormalizePreprocessor`

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

        >>> standardize_preprocessor = StandardizePreprocessor(
        ...     mean_values=[.485, .456, .406],
        ...     std_values=[.229, .224, .225],
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

    @classmethod
    def from_config(
        cls,
        config: StandardizePreprocessorConfig,
    ) -> StandardizePreprocessor:
        """Creates a standardize preprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            standardize preprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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
    """Configuration for the `from_config` class method of `StandardizePreprocessor`

    Attributes:
        mean_values: mean values of the data (per channel)
        std_values: standard deviation values of the data (per channel)
    """
    mean_values: list[float]
    std_values: list[float]
