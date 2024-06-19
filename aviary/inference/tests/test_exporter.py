from pathlib import Path
from unittest.mock import patch

import numpy as np

from aviary.inference.exporter import SegmentationExporter


def test_init() -> None:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    num_workers = 1
    segmentation_exporter = SegmentationExporter(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        num_workers=num_workers,
    )

    assert segmentation_exporter.path == path
    assert segmentation_exporter.tile_size == tile_size
    assert segmentation_exporter.ground_sampling_distance == ground_sampling_distance
    assert segmentation_exporter.epsg_code == epsg_code
    assert segmentation_exporter.field_name == field_name
    assert segmentation_exporter.num_workers == num_workers


@patch('aviary.inference.exporter.segmentation_exporter')
def test_call(
    mocked_segmentation_exporter,
    segmentation_exporter: SegmentationExporter,
) -> None:
    preds = np.ones(shape=(4, 640, 640), dtype=np.uint8)
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    segmentation_exporter(
        preds=preds,
        coordinates=coordinates,
    )

    mocked_segmentation_exporter.assert_called_once_with(
        preds=preds,
        coordinates=coordinates,
        path=segmentation_exporter.path,
        tile_size=segmentation_exporter.tile_size,
        ground_sampling_distance=segmentation_exporter.ground_sampling_distance,
        epsg_code=segmentation_exporter.epsg_code,
        field_name=segmentation_exporter.field_name,
        ignore_background_class=segmentation_exporter._IGNORE_BACKGROUND_CLASS,
        num_workers=segmentation_exporter.num_workers,
    )
