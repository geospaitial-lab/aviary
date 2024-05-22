from typing import cast
from unittest.mock import patch

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pytest

from ..coordinates_filter import (
    duplicates_filter,
    _geospatial_filter_difference,
    _geospatial_filter_intersection,
    mask_filter,
    set_filter,
    _set_filter_difference,
    _set_filter_intersection,
    _set_filter_union,
)
from .data.data_test_coordinates_filter import (
    data_test_duplicates_filter,
    data_test__geospatial_filter_difference,
    data_test__geospatial_filter_intersection,
    data_test_mask_filter,
    data_test__set_filter_difference,
    data_test__set_filter_intersection,
    data_test__set_filter_union,
)
from ....utils.types import (
    Coordinates,
    SetFilterMode,
)


@pytest.mark.skip(reason='Not implemented')
def test_composite_filter() -> None:
    pass


@pytest.mark.parametrize('coordinates, expected', data_test_duplicates_filter)
def test_duplicates_filter(
    coordinates: Coordinates,
    expected: Coordinates,
) -> None:
    filtered_coordinates = duplicates_filter(
        coordinates=coordinates,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@pytest.mark.skip(reason='Not implemented')
def test_geospatial_filter() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test__generate_grid() -> None:
    pass


@pytest.mark.parametrize('coordinates, grid, gdf, expected', data_test__geospatial_filter_difference)
def test__geospatial_filter_difference(
    coordinates: Coordinates,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
    expected: Coordinates,
) -> None:
    filtered_coordinates = _geospatial_filter_difference(
        coordinates=coordinates,
        grid=grid,
        gdf=gdf,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@pytest.mark.parametrize('coordinates, grid, gdf, expected', data_test__geospatial_filter_intersection)
def test__geospatial_filter_intersection(
    coordinates: Coordinates,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
    expected: Coordinates,
) -> None:
    filtered_coordinates = _geospatial_filter_intersection(
        coordinates=coordinates,
        grid=grid,
        gdf=gdf,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@pytest.mark.parametrize('coordinates, mask, expected', data_test_mask_filter)
def test_mask_filter(
    coordinates: Coordinates,
    mask: npt.NDArray[np.bool_],
    expected: Coordinates,
) -> None:
    filtered_coordinates = mask_filter(
        coordinates=coordinates,
        mask=mask,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@patch('aviary._functional.geodata.coordinates_filter._set_filter_union')
@patch('aviary._functional.geodata.coordinates_filter._set_filter_intersection')
@patch('aviary._functional.geodata.coordinates_filter._set_filter_difference')
def test_set_filter(
    mocked_set_filter_difference,
    mocked_set_filter_intersection,
    mocked_set_filter_union,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    additional_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected = 'expected'

    mode = SetFilterMode.DIFFERENCE
    mocked_set_filter_difference.return_value = expected
    filtered_coordinates = set_filter(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
        mode=mode,
    )

    mocked_set_filter_difference.assert_called_once_with(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )
    mocked_set_filter_intersection.assert_not_called()
    mocked_set_filter_union.assert_not_called()
    assert filtered_coordinates == expected

    mocked_set_filter_difference.reset_mock()
    mocked_set_filter_intersection.reset_mock()
    mocked_set_filter_union.reset_mock()

    mode = SetFilterMode.INTERSECTION
    mocked_set_filter_intersection.return_value = expected
    filtered_coordinates = set_filter(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
        mode=mode,
    )

    mocked_set_filter_intersection.assert_called_once_with(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )
    mocked_set_filter_difference.assert_not_called()
    mocked_set_filter_union.assert_not_called()
    assert filtered_coordinates == expected

    mocked_set_filter_difference.reset_mock()
    mocked_set_filter_intersection.reset_mock()
    mocked_set_filter_union.reset_mock()

    mode = SetFilterMode.UNION
    mocked_set_filter_union.return_value = expected
    filtered_coordinates = set_filter(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
        mode=mode,
    )

    mocked_set_filter_union.assert_called_once_with(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )
    mocked_set_filter_difference.assert_not_called()
    mocked_set_filter_intersection.assert_not_called()
    assert filtered_coordinates == expected

    mocked_set_filter_difference.reset_mock()
    mocked_set_filter_intersection.reset_mock()
    mocked_set_filter_union.reset_mock()

    mode = 'invalid_mode'
    mode = cast(SetFilterMode, mode)
    with pytest.raises(ValueError, match='Invalid set filter mode!'):
        set_filter(
            coordinates=coordinates,
            additional_coordinates=additional_coordinates,
            mode=mode,
        )


@pytest.mark.parametrize('coordinates, additional_coordinates, expected', data_test__set_filter_difference)
def test__set_filter_difference(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
    expected: Coordinates,
) -> None:
    filtered_coordinates = _set_filter_difference(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@pytest.mark.parametrize('coordinates, additional_coordinates, expected', data_test__set_filter_intersection)
def test__set_filter_intersection(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
    expected: Coordinates,
) -> None:
    filtered_coordinates = _set_filter_intersection(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)


@pytest.mark.parametrize('coordinates, additional_coordinates, expected', data_test__set_filter_union)
def test__set_filter_union(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
    expected: Coordinates,
) -> None:
    filtered_coordinates = _set_filter_union(
        coordinates=coordinates,
        additional_coordinates=additional_coordinates,
    )

    np.testing.assert_array_equal(filtered_coordinates, expected)