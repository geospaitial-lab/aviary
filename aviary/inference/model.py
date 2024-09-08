from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import onnxruntime as ort
import pydantic
from huggingface_hub import hf_hub_download

if TYPE_CHECKING:
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.inference.model import (
    get_providers,
    onnx_segmentation_model,
)

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError

# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Device,
    GroundSamplingDistance,
)
from aviary.inference.aviary import aviary


class Model(Protocol):
    """Protocol for models

    Models are callables that transform inputs into predictions.

    Currently implemented models:
        - `ONNXSegmentationModel`: ONNX model for segmentation
    """

    def __call__(
        self,
        inputs: npt.NDArray,
    ) -> npt.NDArray:
        """Runs the model.

        Parameters:
            inputs: batched inputs

        Returns:
            batched predictions
        """
        ...


class SegmentationModel:
    """Model for segmentation"""

    def __init__(
        self,
        path: Path,
        ground_sampling_distance: GroundSamplingDistance,
        buffer_size: BufferSize = 0,
        device: Device = Device.CPU,
    ) -> None:
        """
        Parameters:
            path: path to the model
            ground_sampling_distance: ground sampling distance in meters
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)
        """
        self.path = path
        self.ground_sampling_distance = ground_sampling_distance
        self.buffer_size = buffer_size
        self.device = device

    @classmethod
    def from_huggingface(
        cls,
        repo: str,
        path: str,
        ground_sampling_distance: GroundSamplingDistance,
        buffer_size: BufferSize = 0,
        device: Device = Device.CPU,
    ) -> SegmentationModel:
        """Creates a segmentation model from the Hugging Face Hub.

        Parameters:
            repo: repository (Hugging Face Hub, e.g., 'user/repo')
            path: path to the model (Hugging Face Hub)
            ground_sampling_distance: ground sampling distance in meters
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)

        Returns:
            segmentation model
        """
        path = hf_hub_download(
            repo_id=repo,
            filename=path,
        )
        path = Path(path)
        return cls(
            path=path,
            ground_sampling_distance=ground_sampling_distance,
            buffer_size=buffer_size,
            device=device,
        )

    @classmethod
    def from_aviary(
        cls,
        name: str,
        ground_sampling_distance: GroundSamplingDistance,
        buffer_size: BufferSize = 0,
        device: Device = Device.CPU,
    ) -> SegmentationModel:
        """Creates a segmentation model from the name of a model in aviary.

        Parameters:
            name: name of the model
            ground_sampling_distance: ground sampling distance in meters
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)

        Returns:
            segmentation model
        """
        model_card = aviary[name]
        return cls.from_huggingface(
            repo=model_card.repo,
            path=model_card.path,
            ground_sampling_distance=ground_sampling_distance,
            buffer_size=buffer_size,
            device=device,
        )

    @classmethod
    def from_config(
        cls,
        config: SegmentationModelConfig,
    ) -> SegmentationModel:
        """Creates a segmentation model from the configuration.

        Parameters:
            config: configuration

        Returns:
            segmentation model

        Raises:
            AviaryUserError: Invalid configuration
        """
        if config.name is not None:
            return cls.from_aviary(
                name=config.name,
                ground_sampling_distance=config.ground_sampling_distance,
                buffer_size=config.buffer_size,
                device=config.device,
            )

        if config.repo is not None and config.path is not None:
            return cls.from_huggingface(
                repo=config.repo,
                path=config.path,
                ground_sampling_distance=config.ground_sampling_distance,
                buffer_size=config.buffer_size,
                device=config.device,
            )

        if config.path is not None:
            return cls(
                path=Path(config.path),
                ground_sampling_distance=config.ground_sampling_distance,
                buffer_size=config.buffer_size,
                device=config.device,
            )

        message = (
            'Invalid configuration! '
            'config must have one of the following field sets: '
            'name | repo, path | path'
        )
        raise AviaryUserError(message)

    def __call__(
        self,
        inputs: npt.NDArray,
    ) -> npt.NDArray:
        """Runs the model.

        Parameters:
            inputs: batched inputs

        Returns:
            batched predictions
        """
        raise NotImplementedError


class SegmentationModelConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SegmentationModel`

    The configuration must have one of the following field sets:
        - `name`
        - `repo` and `path`
        - `path`

    Attributes:
        path: path to the model (local or Hugging Face Hub)
        repo: repository (Hugging Face Hub, e.g., 'user/repo')
        name: name of the model
        ground_sampling_distance: ground sampling distance in meters
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        device: device ('cpu' or 'cuda')
    """
    path: str | None = None  # don't cast to Path, as it can be a Hugging Face Hub unix path
    repo: str | None = None
    name: str | None = None
    ground_sampling_distance: GroundSamplingDistance
    buffer_size: BufferSize = 0
    device: Device = Device.CPU

    @pydantic.model_validator(mode='after')
    def validate(self) -> SegmentationModelConfig:
        """Validates the configuration."""
        conditions = [
            self.name is not None,
            self.repo is not None and self.path is not None,
            self.path is not None,
        ]

        if any(conditions) is False:
            message = (
                'Invalid configuration! '
                'config must have one of the following field sets: '
                'name | repo, path | path'
            )
            raise ValueError(message)

        return self


class ONNXSegmentationModel(SegmentationModel):
    """ONNX model for segmentation

    Implements the `Model` protocol.
    """

    def __init__(
        self,
        path: Path,
        ground_sampling_distance: GroundSamplingDistance,
        buffer_size: BufferSize = 0,
        device: Device = Device.CPU,
    ) -> None:
        """
        Parameters:
            path: path to the model
            ground_sampling_distance: ground sampling distance in meters
            buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)
        """
        super().__init__(
            path=path,
            ground_sampling_distance=ground_sampling_distance,
            buffer_size=buffer_size,
            device=device,
        )
        self._providers = get_providers(self.device)
        self._model = ort.InferenceSession(
            path_or_bytes=self.path,
            providers=self._providers)
        self._model_input_name = self._model.get_inputs()[0].name
        self._model_output_name = self._model.get_outputs()[0].name

    def __call__(
        self,
        inputs: npt.NDArray,
    ) -> npt.NDArray:
        """Runs the model.

        Parameters:
            inputs: batched inputs

        Returns:
            batched predictions
        """
        return onnx_segmentation_model(
            model=self._model,
            model_input_name=self._model_input_name,
            model_output_name=self._model_output_name,
            inputs=inputs,
            ground_sampling_distance=self.ground_sampling_distance,
            buffer_size=self.buffer_size,
        )
