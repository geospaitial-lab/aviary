import copy
import inspect
import re
from unittest.mock import MagicMock

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import (
    AviaryUserError,
    AviaryUserWarning,
)
from aviary.core.process_area import ProcessArea
from aviary.core.type_aliases import (
    CoordinatesSet,
    TileSize,
)
from aviary.geodata.coordinates_filter import CoordinatesFilter
from tests.core.data.data_test_process_area import (
    data_test_process_area_area,
    data_test_process_area_from_json,
    data_test_process_area_init,
    data_test_process_area_validation,
)


@pytest.mark.parametrize(('coordinates', 'tile_size', 'expected'), data_test_process_area_init)
def test_process_area_init(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    expected: CoordinatesSet,
) -> None:
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    np.testing.assert_array_equal(process_area.coordinates, expected)
    assert process_area.tile_size == tile_size


def test_process_area_init_duplicates() -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, -128], [0, 0]], dtype=np.int32)
    tile_size = 128
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    message = (
        'Invalid coordinates! '
        'coordinates must be an array of unique coordinates. '
        'Duplicates are removed.'
    )
    message = re.escape(message)

    with pytest.warns(AviaryUserWarning, match=message):
        process_area = ProcessArea(
            coordinates=coordinates,
            tile_size=tile_size,
        )

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == tile_size


def test_process_area_mutability() -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    tile_size = 128
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    copied_coordinates = copy.deepcopy(coordinates)
    coordinates += 1

    np.testing.assert_array_equal(process_area.coordinates, copied_coordinates)


@pytest.mark.parametrize(('coordinates', 'tile_size', 'message'), data_test_process_area_validation)
def test_process_area_validation(
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
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_from_bounding_box_defaults() -> None:
    signature = inspect.signature(ProcessArea.from_bounding_box)
    quantize = signature.parameters['quantize'].default

    assert quantize is True


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
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_from_gdf_defaults() -> None:
    signature = inspect.signature(ProcessArea.from_gdf)
    quantize = signature.parameters['quantize'].default

    assert quantize is True


@pytest.mark.parametrize(('json_string', 'expected'), data_test_process_area_from_json)
def test_process_area_from_json(
    json_string: str,
    expected: ProcessArea,
) -> None:
    process_area = ProcessArea.from_json(
        json_string=json_string,
    )

    assert process_area == expected


def test_process_area_from_json_exceptions() -> None:
    json_string = '{"invalid": 0}'
    message = re.escape('Invalid JSON string! json_string must contain the keys coordinates and tile_size.')

    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea.from_json(
            json_string=json_string,
        )


@pytest.mark.skip(reason='Not implemented')
def test_process_area_from_config() -> None:
    pass


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

    other = 'invalid'

    assert process_area != other


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
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_add_exceptions(
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
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_sub_exceptions(
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
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_and_exceptions(
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
    copied_process_area = copy.deepcopy(process_area)

    other_coordinates = (128, -128)
    process_area_ = process_area.append(
        coordinates=other_coordinates,
        inplace=False,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected


def test_process_area_append_duplicate(
    process_area: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    other_coordinates = (0, 0)
    message = re.escape('Invalid coordinates! coordinates is already in the process area.')

    with pytest.warns(AviaryUserWarning, match=message):
        process_area_ = process_area.append(
            coordinates=other_coordinates,
            inplace=False,
        )

    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected


def test_process_area_append_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (128, -128)
    process_area.append(
        coordinates=other_coordinates,
        inplace=True,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_append_duplicate_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (0, 0)
    message = re.escape('Invalid coordinates! coordinates is already in the process area.')

    with pytest.warns(AviaryUserWarning, match=message):
        process_area.append(
            coordinates=other_coordinates,
            inplace=True,
        )

    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_append_defaults() -> None:
    signature = inspect.signature(ProcessArea.append)
    inplace = signature.parameters['inplace'].default

    assert inplace is False


def test_process_area_chunk() -> None:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]], dtype=np.int32)
    tile_size = 128
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    process_areas = process_area.chunk(num_chunks=2)
    expected_coordinates_1 = np.array([[-128, -128], [0, -128], [-128, 0]], dtype=np.int32)
    expected_coordinates_2 = np.array([[0, 0], [128, -128]], dtype=np.int32)
    expected_tile_size = 128
    expected_1 = ProcessArea(
        coordinates=expected_coordinates_1,
        tile_size=expected_tile_size,
    )
    expected_2 = ProcessArea(
        coordinates=expected_coordinates_2,
        tile_size=expected_tile_size,
    )
    expected = [expected_1, expected_2]

    assert process_areas == expected


def test_process_area_filter(
    process_area: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    process_area_ = process_area.filter(
        coordinates_filter=coordinates_filter,
        inplace=False,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected
    coordinates_filter.assert_called_once()


def test_process_area_filter_inplace(
    process_area: ProcessArea,
) -> None:
    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    process_area = process_area.filter(
        coordinates_filter=coordinates_filter,
        inplace=True,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected
    coordinates_filter.assert_called_once()


def test_process_area_filter_defaults() -> None:
    signature = inspect.signature(ProcessArea.filter)
    inplace = signature.parameters['inplace'].default

    assert inplace is False


def test_process_area_remove(
    process_area: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    other_coordinates = (0, 0)
    process_area_ = process_area.remove(
        coordinates=other_coordinates,
        inplace=False,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected


def test_process_area_remove_nonexistent(
    process_area: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    other_coordinates = (128, -128)
    message = re.escape('Invalid coordinates! coordinates is not in the process area.')

    with pytest.warns(AviaryUserWarning, match=message):
        process_area_ = process_area.remove(
            coordinates=other_coordinates,
            inplace=False,
        )

    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected


def test_process_area_remove_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (0, 0)
    process_area.remove(
        coordinates=other_coordinates,
        inplace=True,
    )
    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_remove_nonexistent_inplace(
    process_area: ProcessArea,
) -> None:
    other_coordinates = (128, -128)
    message = re.escape('Invalid coordinates! coordinates is not in the process area.')

    with pytest.warns(AviaryUserWarning, match=message):
        process_area.remove(
            coordinates=other_coordinates,
            inplace=True,
        )

    expected_coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected


def test_process_area_remove_defaults() -> None:
    signature = inspect.signature(ProcessArea.remove)
    inplace = signature.parameters['inplace'].default

    assert inplace is False


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


@pytest.mark.skip(reason='Not implemented')
def test_process_area_config() -> None:
    pass
