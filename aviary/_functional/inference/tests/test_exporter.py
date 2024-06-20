from pathlib import Path
from unittest.mock import patch

import dask
import numpy as np
import pytest

from aviary._functional.inference.exporter import _segmentation_exporter_task
# noinspection PyProtectedMember
from aviary._utils.types import SegmentationExporterMode


@pytest.mark.skip(reason='Not implemented')
def test_segmentation_exporter() -> None:
    pass


@patch('aviary._functional.inference.exporter._export_gdf')
@patch('aviary._functional.inference.exporter._vectorize_preds')
def test__segmentation_exporter_task(
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
    gpkg_name = 'output.gpkg'
    mode = SegmentationExporterMode.GPKG
    expected_gdf = 'expected_gdf'
    mocked__vectorize_preds.return_value = expected_gdf
    dask.compute(
        _segmentation_exporter_task(
            preds=preds,
            x_min=x_min,
            y_min=y_min,
            path=path,
            tile_size=tile_size,
            ground_sampling_distance=ground_sampling_distance,
            epsg_code=epsg_code,
            field_name=field_name,
            ignore_background_class=ignore_background_class,
            gpkg_name=gpkg_name,
            mode=mode,
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
        path=path,
        x_min=x_min,
        y_min=y_min,
        gpkg_name=gpkg_name,
        mode=mode,
    )


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf_feather() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf_gpkg() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__vectorize_preds() -> None:
    pass
