import re
from unittest.mock import MagicMock, patch

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pytest

# noinspection PyProtectedMember
from aviary._functional.utils.coordinates_filter import (
    _geospatial_filter_difference,
    _geospatial_filter_intersection,
    _set_filter_difference,
    _set_filter_intersection,
    _set_filter_union,
    duplicates_filter,
    mask_filter,
    set_filter,
)
from aviary.core.enums import SetFilterMode
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import CoordinatesSet
from tests._functional.utils.data.data_test_coordinates_filter import (
    data_test__geospatial_filter_difference,
    data_test__geospatial_filter_intersection,
    data_test__set_filter_difference,
    data_test__set_filter_intersection,
    data_test__set_filter_union,
    data_test_duplicates_filter,
    data_test_mask_filter,
)


@pytest.mark.skip(reason='Not implemented')
def test_composite_filter() -> None:
    pass


@pytest.mark.parametrize(('coordinates', 'expected'), data_test_duplicates_filter)
def test_duplicates_filter(
    coordinates: CoordinatesSet,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = duplicates_filter(
        coordinates=coordinates,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@pytest.mark.skip(reason='Not implemented')
def test_geospatial_filter() -> None:
    pass


@pytest.mark.parametrize(('coordinates', 'grid', 'gdf', 'expected'), data_test__geospatial_filter_difference)
def test__geospatial_filter_difference(
    coordinates: CoordinatesSet,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = _geospatial_filter_difference(
        coordinates=coordinates,
        grid=grid,
        gdf=gdf,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@pytest.mark.parametrize(('coordinates', 'grid', 'gdf', 'expected'), data_test__geospatial_filter_intersection)
def test__geospatial_filter_intersection(
    coordinates: CoordinatesSet,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = _geospatial_filter_intersection(
        coordinates=coordinates,
        grid=grid,
        gdf=gdf,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@pytest.mark.parametrize(('coordinates', 'mask', 'expected'), data_test_mask_filter)
def test_mask_filter(
    coordinates: CoordinatesSet,
    mask: npt.NDArray[np.bool_],
    expected: CoordinatesSet,
) -> None:
    coordinates_ = mask_filter(
        coordinates=coordinates,
        mask=mask,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@patch('aviary._functional.utils.coordinates_filter._set_filter_difference')
def test_set_filter_difference(
    mocked_set_filter_difference: MagicMock,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.DIFFERENCE

    expected = 'expected'
    mocked_set_filter_difference.return_value = expected

    coordinates_ = set_filter(
        coordinates=coordinates,
        other=other,
        mode=mode,
    )

    assert coordinates_ == expected
    mocked_set_filter_difference.assert_called_once_with(
        coordinates=coordinates,
        other=other,
    )


@patch('aviary._functional.utils.coordinates_filter._set_filter_intersection')
def test_set_filter_intersection(
    mocked_set_filter_intersection: MagicMock,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.INTERSECTION

    expected = 'expected'
    mocked_set_filter_intersection.return_value = expected

    coordinates_ = set_filter(
        coordinates=coordinates,
        other=other,
        mode=mode,
    )

    assert coordinates_ == expected
    mocked_set_filter_intersection.assert_called_once_with(
        coordinates=coordinates,
        other=other,
    )


@patch('aviary._functional.utils.coordinates_filter._set_filter_union')
def test_set_filter_union(
    mocked_set_filter_union: MagicMock,
) -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.UNION

    expected = 'expected'
    mocked_set_filter_union.return_value = expected

    coordinates_ = set_filter(
        coordinates=coordinates,
        other=other,
        mode=mode,
    )

    assert coordinates_ == expected
    mocked_set_filter_union.assert_called_once_with(
        coordinates=coordinates,
        other=other,
    )


def test_set_filter_exceptions() -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = 'invalid'

    message = re.escape('Invalid mode!')

    with pytest.raises(AviaryUserError, match=message):
        _ = set_filter(
            coordinates=coordinates,
            other=other,
            mode=mode,
        )


@pytest.mark.parametrize(('coordinates', 'other', 'expected'), data_test__set_filter_difference)
def test__set_filter_difference(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = _set_filter_difference(
        coordinates=coordinates,
        other=other,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@pytest.mark.parametrize(('coordinates', 'other', 'expected'), data_test__set_filter_intersection)
def test__set_filter_intersection(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = _set_filter_intersection(
        coordinates=coordinates,
        other=other,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)


@pytest.mark.parametrize(('coordinates', 'other', 'expected'), data_test__set_filter_union)
def test__set_filter_union(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
    expected: CoordinatesSet,
) -> None:
    coordinates_ = _set_filter_union(
        coordinates=coordinates,
        other=other,
    )

    np.testing.assert_array_equal(coordinates_, expected)
    assert id(coordinates_) != id(coordinates)
