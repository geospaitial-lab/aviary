from pathlib import Path

import pytest

# noinspection PyProtectedMember
from aviary._utils.types import SegmentationExporterMode
from aviary.inference.aviary import (
    Aviary,
    Channels,
    ModelCard,
    Type,
)
from aviary.inference.exporter import SegmentationExporter


@pytest.fixture(scope='session')
def model_card() -> ModelCard:
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
    return ModelCard(
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


@pytest.fixture(scope='session')
def aviary(
    model_card: ModelCard,
) -> Aviary:
    model_cards = [model_card] * 3
    return Aviary(
        model_cards=model_cards,
    )


@pytest.fixture(scope='session')
def segmentation_exporter() -> SegmentationExporter:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    mode = SegmentationExporterMode.GPKG
    num_workers = 4
    return SegmentationExporter(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        mode=mode,
        num_workers=num_workers,
    )
