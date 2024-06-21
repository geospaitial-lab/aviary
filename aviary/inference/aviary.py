from dataclasses import dataclass
from enum import Enum

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError


class Channels(Enum):
    """
    Attributes:
        RGB: Red, Green, Blue
        NIR: Near Infrared
    """
    RGB = 'rgb'
    NIR = 'nir'


class Framework(Enum):
    """
    Attributes:
        ONNX: Open Neural Network Exchange
        TORCH: PyTorch
    """
    ONNX = 'onnx'
    TORCH = 'torch'


class Type(Enum):
    """
    Attributes:
        SEGMENTATION: segmentation
    """
    SEGMENTATION = 'segmentation'


@dataclass
class Model:
    """
    Attributes:
        name: name of the model
        repo: repository (huggingface hub, e.g. 'user/repo')
        path: path to the model (huggingface hub)
        framework: framework (`ONNX` or `TORCH`)
        type: type (`SEGMENTATION`)
        required_channels: required channels (`RGB`, `NIR`)
        num_channels: number of channels
        ground_sampling_distance: ground sampling distance in meters
        num_classes: number of classes
        min_values: minimum values of the data (per channel)
        max_values: maximum values of the data (per channel)
        mean_values: mean values of the data (per channel)
        std_values: standard deviation values of the data (per channel)
        description: description
    """
    name: str
    repo: str
    path: str
    framework: Framework
    type: Type
    required_channels: list[Channels]
    num_channels: int
    ground_sampling_distance: float
    num_classes: int
    min_values: list[float]
    max_values: list[float]
    mean_values: list[float] = None
    std_values: list[float] = None
    description: str = None


@dataclass
class Aviary:
    """
    Attributes:
        models: models
    """
    models: list[Model]

    def __getitem__(
        self,
        name: str,
    ) -> Model:
        """Returns the model given its name.

        Parameters:
            name: name of the model

        Returns:
            model

        Raises:
            AviaryUserError: Invalid name of the model
        """
        for model in self.models:
            if model.name == name:
                return model

        model_names = ', '.join([model.name for model in self.models])
        message = (
            'Invalid name of the model! '
            f'Available models: {model_names}'
        )
        raise AviaryUserError(message)
