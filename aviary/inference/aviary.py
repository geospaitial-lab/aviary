from dataclasses import dataclass
from enum import Enum

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError


class Channels(Enum):
    """
    Attributes:
        RGB: red, green, blue
        NIR: near-infrared
    """
    RGB = 'rgb'
    NIR = 'nir'


class Type(Enum):
    """
    Attributes:
        SEGMENTATION: segmentation
    """
    SEGMENTATION = 'segmentation'


@dataclass
class ModelCard:
    """
    Attributes:
        name: name of the model
        repo: repository (Hugging Face Hub, e.g., 'user/repo')
        path: path to the model (Hugging Face Hub)
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
        model_cards: model cards
    """
    model_cards: list[ModelCard]

    def __getitem__(
        self,
        name: str,
    ) -> ModelCard:
        """Returns the model card.

        Parameters:
            name: name of the model

        Returns:
            model card

        Raises:
            AviaryUserError: Invalid name of the model
        """
        for model_card in self.model_cards:
            if model_card.name == name:
                return model_card

        model_names = ', '.join([model_card.name for model_card in self.model_cards])
        message = (
            'Invalid name of the model! '
            f'Available model cards: {model_names}'
        )
        raise AviaryUserError(message)


sparrow = ModelCard(
    name='sparrow',
    repo='geospaitial-lab/sparrow',
    path='models/sparrow.onnx',
    type=Type.SEGMENTATION,
    required_channels=[Channels.RGB, Channels.NIR],
    num_channels=4,
    ground_sampling_distance=.2,
    num_classes=2,
    min_values=[0.] * 4,
    max_values=[255.] * 4,
    description='Impervious surfaces',
)  # pragma: no cover


aviary = Aviary(
    model_cards=[
        sparrow,
    ],
)  # pragma: no cover
