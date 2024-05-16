from pathlib import Path
from unittest.mock import patch

import dask
import numpy as np
import pytest

from ..vectorizer import (
    _vectorizer_element,
)


@pytest.mark.skip(reason='Not implemented')
def test_vectorizer() -> None:
    pass


@patch('src.functional.geodata.vectorizer._export_gdf')
@patch('src.functional.geodata.vectorizer._vectorize_preds')
def test__vectorizer_element(
    mocked__vectorize_preds,
    mocked__export_gdf,
) -> None:
    preds = np.ones(shape=(640, 640), dtype=np.uint8)
    x_min = -128
    y_min = -128
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    ignore_background_class = True
    expected_gdf = 'expected_gdf'
    mocked__vectorize_preds.return_value = expected_gdf
    dask.compute(
        _vectorizer_element(
            preds=preds,
            x_min=x_min,
            y_min=y_min,
            path=path,
            tile_size=tile_size,
            ground_sampling_distance=ground_sampling_distance,
            epsg_code=epsg_code,
            field_name=field_name,
            ignore_background_class=ignore_background_class,
        )
    )

    mocked__vectorize_preds.assert_called_once_with(
        preds=preds,
        x_min=x_min,
        y_min=y_min,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        ignore_background_class=ignore_background_class,
    )
    mocked__export_gdf.assert_called_once_with(
        gdf=expected_gdf,
        x_min=x_min,
        y_min=y_min,
        path=path,
    )


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__vectorize_preds() -> None:
    pass
