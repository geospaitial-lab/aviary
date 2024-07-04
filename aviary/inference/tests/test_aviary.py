import pytest

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError
from aviary.inference.aviary import (
    Aviary,
    Channels,
    ModelCard,
    Type,
)


def test_model_card_init() -> None:
    name = 'name'
    repo = 'repo'
    path = 'path'
    type_ = Type.SEGMENTATION
    required_channels = [Channels.RGB, Channels.NIR]
    num_channels = 4
    ground_sampling_distance = .2
    num_classes = 3
    min_values = [0.] * 4
    max_values = [255.] * 4
    mean_values = [.485, .456, .406, .5]
    std_values = [.229, .224, .225, .5]
    description = 'description'
    model = ModelCard(
        name=name,
        repo=repo,
        path=path,
        type=type_,
        required_channels=required_channels,
        num_channels=num_channels,
        ground_sampling_distance=ground_sampling_distance,
        num_classes=num_classes,
        min_values=min_values,
        max_values=max_values,
        mean_values=mean_values,
        std_values=std_values,
        description=description,
    )

    assert model.name == name
    assert model.repo == repo
    assert model.path == path
    assert model.type == type_
    assert model.required_channels == required_channels
    assert model.num_channels == num_channels
    assert model.ground_sampling_distance == ground_sampling_distance
    assert model.num_classes == num_classes
    assert model.min_values == min_values
    assert model.max_values == max_values
    assert model.mean_values == mean_values
    assert model.std_values == std_values
    assert model.description == description


def test_aviary_init(
    model_card: ModelCard,
) -> None:
    model_cards = [model_card] * 3
    aviary = Aviary(
        model_cards=model_cards,
    )

    assert aviary.model_cards == model_cards


def test_aviary_getitem(
    aviary: Aviary,
    model_card: ModelCard,
) -> None:
    name = model_card.name
    assert aviary[name] == model_card


def test_aviary_getitem_exceptions(
    aviary: Aviary,
) -> None:
    name = 'invalid_name'
    model_names = ', '.join([model_card.name for model_card in aviary.model_cards])
    message = (
        'Invalid name of the model! '
        f'Available model cards: {model_names}'
    )
    with pytest.raises(AviaryUserError, match=message):
        _ = aviary[name]
