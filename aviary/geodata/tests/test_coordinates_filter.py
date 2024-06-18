from unittest.mock import MagicMock, patch

import geopandas as gpd
import geopandas.testing
import numpy as np

# noinspection PyProtectedMember
from aviary._utils.types import (
    GeospatialFilterMode,
    SetFilterMode,
)

from aviary.geodata.coordinates_filter import (
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

    assert composite_filter.coordinates_filters == coordinates_filters


@patch('aviary.geodata.coordinates_filter.composite_filter')
def test_composite_filter_call(
    mocked_composite_filter,
    composite_filter: CompositeFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'
    mocked_composite_filter.return_value = expected
    filtered_coordinates = composite_filter(
        coordinates=coordinates,
    )

    mocked_composite_filter.assert_called_once_with(
        coordinates=coordinates,
        coordinates_filters=composite_filter.coordinates_filters,
    )
    assert filtered_coordinates == expected


def test_duplicates_filter_init() -> None:
    _ = DuplicatesFilter()


@patch('aviary.geodata.coordinates_filter.duplicates_filter')
def test_duplicates_filter_call(
    mocked_duplicates_filter,
    duplicates_filter: DuplicatesFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'
    mocked_duplicates_filter.return_value = expected
    filtered_coordinates = duplicates_filter(
        coordinates=coordinates,
    )

    mocked_duplicates_filter.assert_called_once_with(
        coordinates=coordinates,
    )
    assert filtered_coordinates == expected


def test_geospatial_filter_init() -> None:
    tile_size = 128
    epsg_code = 25832
    geometry = []
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    mode = GeospatialFilterMode.DIFFERENCE
    geospatial_filter = GeospatialFilter(
        tile_size=tile_size,
        epsg_code=epsg_code,
        gdf=gdf,
        mode=mode,
    )

    assert geospatial_filter.tile_size == tile_size
    assert geospatial_filter.epsg_code == epsg_code
    gpd.testing.assert_geodataframe_equal(geospatial_filter.gdf, gdf)
    assert geospatial_filter.mode == mode


@patch('aviary.geodata.coordinates_filter.geospatial_filter')
def test_geospatial_filter_call(
    mocked_geospatial_filter,
    geospatial_filter: GeospatialFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'
    mocked_geospatial_filter.return_value = expected
    filtered_coordinates = geospatial_filter(
        coordinates=coordinates,
    )

    mocked_geospatial_filter.assert_called_once_with(
        coordinates=coordinates,
        tile_size=geospatial_filter.tile_size,
        epsg_code=geospatial_filter.epsg_code,
        gdf=geospatial_filter.gdf,
        mode=geospatial_filter.mode,
    )
    assert filtered_coordinates == expected


def test_mask_filter_init() -> None:
    mask = np.array([0, 1, 0, 1], dtype=np.bool_)
    mask_filter = MaskFilter(
        mask=mask,
    )

    np.testing.assert_array_equal(mask_filter.mask, mask)


@patch('aviary.geodata.coordinates_filter.mask_filter')
def test_mask_filter_call(
    mocked_mask_filter,
    mask_filter: MaskFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'
    mocked_mask_filter.return_value = expected
    filtered_coordinates = mask_filter(
        coordinates=coordinates,
    )

    mocked_mask_filter.assert_called_once_with(
        coordinates=coordinates,
        mask=mask_filter.mask,
    )
    assert filtered_coordinates == expected


def test_set_filter_init() -> None:
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.DIFFERENCE
    set_filter = SetFilter(
        other=other,
        mode=mode,
    )

    np.testing.assert_array_equal(set_filter.other, other)
    assert set_filter.mode == mode


@patch('aviary.geodata.coordinates_filter.set_filter')
def test_set_filter_call(
    mocked_set_filter,
    set_filter: SetFilter,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'
    mocked_set_filter.return_value = expected
    filtered_coordinates = set_filter(
        coordinates=coordinates,
    )

    mocked_set_filter.assert_called_once_with(
        coordinates=coordinates,
        other=set_filter.other,
        mode=set_filter.mode,
    )
    assert filtered_coordinates == expected
