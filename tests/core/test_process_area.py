import re

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.process_area import ProcessArea
from aviary.core.type_aliases import (
    CoordinatesSet,
    TileSize,
)
from tests.core.data.data_test_process_area import (
    data_test_process_area_area,
    data_test_process_area_init_exceptions,
)


def test_process_area_init() -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    tile_size = 128
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    np.testing.assert_array_equal(process_area.coordinates, coordinates)
    assert process_area.tile_size == tile_size

    coordinates = None
    tile_size = 128
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    expected = np.empty(
        shape=(0, 2),
        dtype=np.int32,
    )

    np.testing.assert_array_equal(process_area.coordinates, expected)
    assert process_area.tile_size == tile_size


@pytest.mark.parametrize(('coordinates', 'tile_size', 'message'), data_test_process_area_init_exceptions)
def test_process_area_init_exceptions(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea(
            coordinates=coordinates,
            tile_size=tile_size,
        )


@pytest.mark.parametrize(('process_area', 'expected'), data_test_process_area_area)
def test_process_area_area(
    process_area: ProcessArea,
    expected: int,
) -> None:
    assert process_area.area == expected


def test_process_area_from_bounding_box() -> None:
    x_min = -128
    y_min = -128
    x_max = 128
    y_max = 128
    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )
    tile_size = 128
    quantize = True
    process_area = ProcessArea.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    expected = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    np.testing.assert_array_equal(process_area.coordinates, expected)
    assert process_area.tile_size == tile_size


def test_process_area_from_gdf() -> None:
    geometry = [box(-128, -128, 128, 128)]
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    tile_size = 128
    quantize = True
    process_area = ProcessArea.from_gdf(
        gdf=gdf,
        tile_size=tile_size,
        quantize=quantize,
    )
    expected = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    np.testing.assert_array_equal(process_area.coordinates, expected)
    assert process_area.tile_size == tile_size


def test_process_area_from_json() -> None:
    json_string = '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]], "tile_size": 128}'
    process_area = ProcessArea.from_json(
        json_string=json_string,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size

    json_string = '{"coordinates": [], "tile_size": 128}'
    process_area = ProcessArea.from_json(
        json_string=json_string,
    )
    expected_coordinates = np.empty(
        shape=(0, 2),
        dtype=np.int32,
    )
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_eq(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    other_tile_size = 128
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )

    assert process_area == other_process_area

    other_process_area = ProcessArea(
        coordinates=None,
        tile_size=other_tile_size,
    )

    assert process_area != other_process_area


def test_process_area_len(
    process_area: ProcessArea,
) -> None:
    expected = 4

    assert len(process_area) == expected


def test_process_area_getitem(
    process_area: ProcessArea,
) -> None:
    expected_coordinates_1 = (-128, -128)
    expected_coordinates_2 = (0, -128)
    expected_coordinates_3 = (-128, 0)
    expected_coordinates_4 = (0, 0)

    assert process_area[0] == expected_coordinates_1
    assert process_area[1] == expected_coordinates_2
    assert process_area[2] == expected_coordinates_3
    assert process_area[3] == expected_coordinates_4
    assert process_area[-1] == expected_coordinates_4
    assert process_area[-2] == expected_coordinates_3
    assert process_area[-3] == expected_coordinates_2
    assert process_area[-4] == expected_coordinates_1


def test_process_area_getitem_slice(
    process_area: ProcessArea,
) -> None:
    expected_coordinates_1 = np.array([[-128, -128], [0, -128]], dtype=np.int32)
    expected_coordinates_2 = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    expected_coordinates_3 = np.array([[0, -128], [-128, 0]], dtype=np.int32)
    expected_coordinates_4 = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

    np.testing.assert_array_equal(process_area[:2].coordinates, expected_coordinates_1)
    np.testing.assert_array_equal(process_area[2:].coordinates, expected_coordinates_2)
    np.testing.assert_array_equal(process_area[1:-1].coordinates, expected_coordinates_3)
    np.testing.assert_array_equal(process_area[:].coordinates, expected_coordinates_4)


def test_process_area_iter(
    process_area: ProcessArea,
) -> None:
    expected = [
        (-128, -128),
        (0, -128),
        (-128, 0),
        (0, 0),
    ]

    assert list(process_area) == expected


def test_process_area_add(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 128
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    process_area = process_area + other_process_area
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_add_exception(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 64
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    message = re.escape('Invalid other! The tile sizes of the process areas must be equal.')

    with pytest.raises(AviaryUserError, match=message):
        _ = process_area + other_process_area


def test_process_area_sub(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 128
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    process_area = process_area - other_process_area
    expected_coordinates = np.array([[-128, -128], [0, -128]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_sub_exception(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 64
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    message = re.escape('Invalid other! The tile sizes of the process areas must be equal.')

    with pytest.raises(AviaryUserError, match=message):
        _ = process_area - other_process_area


def test_process_area_and(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 128
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    process_area = process_area & other_process_area
    expected_coordinates = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_and_exception(
    process_area: ProcessArea,
) -> None:
    other_coordinates = np.array([[-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32)
    other_tile_size = 64
    other_process_area = ProcessArea(
        coordinates=other_coordinates,
        tile_size=other_tile_size,
    )
    message = re.escape('Invalid other! The tile sizes of the process areas must be equal.')

    with pytest.raises(AviaryUserError, match=message):
        _ = process_area & other_process_area


def test_process_area_append(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (128, -128)
    process_area = process_area.append(other_coordinates)
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_append_duplicate(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (0, 0)
    process_area = process_area.append(other_coordinates)
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_append_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (128, -128)
    process_area.append(other_coordinates, inplace=True)
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


def test_process_area_append_duplicate_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (0, 0)
    process_area.append(other_coordinates, inplace=True)
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


@pytest.mark.skip(reason='Not implemented')
def test_process_area_chunk() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test_process_area_filter() -> None:
    pass


def test_process_area_to_gdf(
    process_area: ProcessArea,
) -> None:
    epsg_code = 25832
    gdf = process_area.to_gdf(
        epsg_code=epsg_code,
    )
    expected_geometry = [
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ]
    expected_epsg_code = 25832
    expected = gpd.GeoDataFrame(
        geometry=expected_geometry,
        crs=f'EPSG:{expected_epsg_code}',
    )

    gpd.testing.assert_geodataframe_equal(gdf, expected)


def test_process_area_to_json(
    process_area: ProcessArea,
) -> None:
    json_string = process_area.to_json()
    expected = '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]], "tile_size": 128}'

    assert json_string == expected
