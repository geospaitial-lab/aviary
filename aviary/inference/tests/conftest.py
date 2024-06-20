from pathlib import Path

import pytest

# noinspection PyProtectedMember
from aviary._utils.types import SegmentationExporterMode
from aviary.inference.exporter import SegmentationExporter


@pytest.fixture(scope='session')
def segmentation_exporter() -> SegmentationExporter:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    mode = SegmentationExporterMode.GPKG
    num_workers = 1
    return SegmentationExporter(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        mode=mode,
        num_workers=num_workers,
    )
