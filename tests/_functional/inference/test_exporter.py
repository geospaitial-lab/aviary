from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import dask
import geopandas as gpd
import numpy as np
import pytest

# noinspection PyProtectedMember
from aviary._functional.inference.exporter import (
    _export_gdf,
    _segmentation_exporter_task,
)

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError

# noinspection PyProtectedMember
from aviary._utils.types import SegmentationExporterMode


@pytest.mark.skip(reason='Not implemented')
def test_segmentation_exporter() -> None:
    pass


@patch('aviary._functional.inference.exporter._export_gdf')
@patch('aviary._functional.inference.exporter._vectorize_preds')
def test__segmentation_exporter_task(
    mocked__vectorize_preds: MagicMock,
    mocked__export_gdf: MagicMock,
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
    json_name = 'processed_coordinates.json'
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
            json_name=json_name,
            mode=mode,
        ),
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
        json_name=json_name,
        mode=mode,
    )


@patch('aviary._functional.inference.exporter._export_coordinates_json')
@patch('aviary._functional.inference.exporter._export_gdf_gpkg')
@patch('aviary._functional.inference.exporter._export_gdf_feather')
def test__export_gdf(
    mocked__export_gdf_feather: MagicMock,
    mocked__export_gdf_gpkg: MagicMock,
    mocked__export_coordinates_json: MagicMock,
) -> None:
    gdf = MagicMock(spec=gpd.GeoDataFrame)
    path = Path('test')
    x_min = -128
    y_min = -128
    gpkg_name = 'output.gpkg'
    json_name = 'processed_coordinates.json'

    mode = SegmentationExporterMode.FEATHER
    _export_gdf(
        gdf=gdf,
        path=path,
        x_min=x_min,
        y_min=y_min,
        gpkg_name=gpkg_name,
        json_name=json_name,
        mode=mode,
    )

    mocked__export_gdf_feather.assert_called_once_with(
        gdf=gdf,
        path=path,
        x_min=x_min,
        y_min=y_min,
    )
    mocked__export_gdf_gpkg.assert_not_called()
    mocked__export_coordinates_json.assert_called_once_with(
        path=path,
        x_min=x_min,
        y_min=y_min,
        json_name=json_name,
    )

    mocked__export_gdf_feather.reset_mock()
    mocked__export_gdf_gpkg.reset_mock()
    mocked__export_coordinates_json.reset_mock()

    mode = SegmentationExporterMode.GPKG
    _export_gdf(
        gdf=gdf,
        path=path,
        x_min=x_min,
        y_min=y_min,
        gpkg_name=gpkg_name,
        mode=mode,
    )

    mocked__export_gdf_gpkg.assert_called_once_with(
        gdf=gdf,
        path=path,
        gpkg_name=gpkg_name,
    )
    mocked__export_gdf_feather.assert_not_called()
    mocked__export_coordinates_json.assert_called_once_with(
        path=path,
        x_min=x_min,
        y_min=y_min,
        json_name=json_name,
    )

    mocked__export_gdf_feather.reset_mock()
    mocked__export_gdf_gpkg.reset_mock()
    mocked__export_coordinates_json.reset_mock()

    mode = 'invalid mode'
    mode = cast(SegmentationExporterMode, mode)
    message = 'Invalid segmentation exporter mode!'
    with pytest.raises(AviaryUserError, match=message):
        _export_gdf(
            gdf=gdf,
            path=path,
            x_min=x_min,
            y_min=y_min,
            gpkg_name=gpkg_name,
            mode=mode,
        )


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf_feather() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__export_gdf_gpkg() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__export_coordinates_json() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__vectorize_preds() -> None:
    pass
