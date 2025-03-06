from unittest.mock import MagicMock, patch

import geopandas as gpd
import geopandas.testing
import numpy as np

from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.utils.coordinates_filter import (
    CompositeFilter,
    CoordinatesFilter,
    DuplicatesFilter,
    GeospatialFilter,
    MaskFilter,
    SetFilter,
)


def test_composite_filter_init() -> None:
    coordinates_filters = [
        MagicMock(spec=CoordinatesFilter),
        MagicMock(spec=CoordinatesFilter),
        MagicMock(spec=CoordinatesFilter),
    ]

    composite_filter = CompositeFilter(
        coordinates_filters=coordinates_filters,
    )

    assert composite_filter._coordinates_filters == coordinates_filters


@patch('aviary.utils.coordinates_filter.composite_filter')
def test_composite_filter_call(
    mocked_composite_filter: MagicMock,
    composite_filter: CompositeFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    expected = 'expected'
    mocked_composite_filter.return_value = expected

    coordinates_ = composite_filter(
        coordinates=coordinates,
    )

    assert coordinates_ == expected
    mocked_composite_filter.assert_called_once_with(
        coordinates=coordinates,
        coordinates_filters=composite_filter._coordinates_filters,
    )


def test_duplicates_filter_init() -> None:
    _ = DuplicatesFilter()


@patch('aviary.utils.coordinates_filter.duplicates_filter')
def test_duplicates_filter_call(
    mocked_duplicates_filter: MagicMock,
    duplicates_filter: DuplicatesFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    expected = 'expected'
    mocked_duplicates_filter.return_value = expected

    coordinates_ = duplicates_filter(
        coordinates=coordinates,
    )

    assert coordinates_ == expected
    mocked_duplicates_filter.assert_called_once_with(
        coordinates=coordinates,
    )


def test_geospatial_filter_init() -> None:
    tile_size = 128
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    mode = GeospatialFilterMode.DIFFERENCE

    geospatial_filter = GeospatialFilter(
        tile_size=tile_size,
        gdf=gdf,
        mode=mode,
    )

    assert geospatial_filter._tile_size == tile_size
    gpd.testing.assert_geodataframe_equal(geospatial_filter._gdf, gdf)
    assert geospatial_filter._mode == mode


@patch('aviary.utils.coordinates_filter.geospatial_filter')
def test_geospatial_filter_call(
    mocked_geospatial_filter: MagicMock,
    geospatial_filter: GeospatialFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    expected = 'expected'
    mocked_geospatial_filter.return_value = expected

    coordinates_ = geospatial_filter(
        coordinates=coordinates,
    )

    assert coordinates_ == expected
    mocked_geospatial_filter.assert_called_once_with(
        coordinates=coordinates,
        tile_size=geospatial_filter._tile_size,
        gdf=geospatial_filter._gdf,
        mode=geospatial_filter._mode,
    )


def test_mask_filter_init() -> None:
    mask = np.array([0, 1, 0, 1], dtype=np.bool_)

    mask_filter = MaskFilter(
        mask=mask,
    )

    np.testing.assert_array_equal(mask_filter._mask, mask)


@patch('aviary.utils.coordinates_filter.mask_filter')
def test_mask_filter_call(
    mocked_mask_filter: MagicMock,
    mask_filter: MaskFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    expected = 'expected'
    mocked_mask_filter.return_value = expected

    coordinates_ = mask_filter(
        coordinates=coordinates,
    )

    assert coordinates_ == expected
    mocked_mask_filter.assert_called_once_with(
        coordinates=coordinates,
        mask=mask_filter._mask,
    )


def test_set_filter_init() -> None:
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.DIFFERENCE

    set_filter = SetFilter(
        other=other,
        mode=mode,
    )

    np.testing.assert_array_equal(set_filter._other, other)
    assert set_filter._mode == mode


@patch('aviary.utils.coordinates_filter.set_filter')
def test_set_filter_call(
    mocked_set_filter: MagicMock,
    set_filter: SetFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    expected = 'expected'
    mocked_set_filter.return_value = expected

    coordinates_ = set_filter(
        coordinates=coordinates,
    )

    assert coordinates_ == expected
    mocked_set_filter.assert_called_once_with(
        coordinates=coordinates,
        other=set_filter._other,
        mode=set_filter._mode,
    )
