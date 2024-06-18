from pathlib import Path
from unittest.mock import patch

import numpy as np

from aviary.geodata.vectorizer import Vectorizer


def test_init() -> None:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    num_workers = 1
    vectorizer = Vectorizer(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        num_workers=num_workers,
    )

    assert vectorizer.path == path
    assert vectorizer.tile_size == tile_size
    assert vectorizer.ground_sampling_distance == ground_sampling_distance
    assert vectorizer.epsg_code == epsg_code
    assert vectorizer.field_name == field_name
    assert vectorizer.num_workers == num_workers


@patch('aviary.geodata.vectorizer.vectorizer')
def test_call(
    mocked_vectorizer,
    vectorizer: Vectorizer,
) -> None:
    preds = np.ones(shape=(4, 640, 640), dtype=np.uint8)
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    vectorizer(
        preds=preds,
        coordinates=coordinates,
    )

    mocked_vectorizer.assert_called_once_with(
        preds=preds,
        coordinates=coordinates,
        path=vectorizer.path,
        tile_size=vectorizer.tile_size,
        ground_sampling_distance=vectorizer.ground_sampling_distance,
        epsg_code=vectorizer.epsg_code,
        field_name=vectorizer.field_name,
        ignore_background_class=vectorizer._IGNORE_BACKGROUND_CLASS,
        num_workers=vectorizer.num_workers,
    )
