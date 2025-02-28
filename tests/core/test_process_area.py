import copy
import inspect
import pickle
from unittest.mock import MagicMock

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.process_area import ProcessArea
from aviary.core.type_aliases import (
    Coordinates,
    CoordinatesSet,
    TileSize,
)
from aviary.geodata.coordinates_filter import CoordinatesFilter
from tests.core.data.data_test_process_area import (
    data_test_process_area_add,
    data_test_process_area_add_exceptions,
    data_test_process_area_and,
    data_test_process_area_and_exceptions,
    data_test_process_area_append,
    data_test_process_area_append_inplace,
    data_test_process_area_append_inplace_return,
    data_test_process_area_area,
    data_test_process_area_bool,
    data_test_process_area_chunk,
    data_test_process_area_chunk_exceptions,
    data_test_process_area_contains,
    data_test_process_area_eq,
    data_test_process_area_from_bounding_box,
    data_test_process_area_from_bounding_box_exceptions,
    data_test_process_area_from_gdf,
    data_test_process_area_from_gdf_exceptions,
    data_test_process_area_from_json,
    data_test_process_area_from_json_exceptions,
    data_test_process_area_from_process_areas,
    data_test_process_area_from_process_areas_exceptions,
    data_test_process_area_getitem,
    data_test_process_area_getitem_slice,
    data_test_process_area_init,
    data_test_process_area_init_exceptions,
    data_test_process_area_remove,
    data_test_process_area_remove_inplace,
    data_test_process_area_remove_inplace_return,
    data_test_process_area_sub,
    data_test_process_area_sub_exceptions,
)


@pytest.mark.parametrize(
    (
        'coordinates',
        'tile_size',
        'expected_coordinates',
        'expected_tile_size',
    ),
    data_test_process_area_init,
)
def test_process_area_init(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    expected_coordinates: CoordinatesSet,
    expected_tile_size: TileSize,
) -> None:
    process_area = ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    np.testing.assert_array_equal(process_area.coordinates, expected_coordinates)
    assert process_area.tile_size == expected_tile_size


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


def test_process_area_mutability(
    process_area_coordinates: CoordinatesSet,
) -> None:
    tile_size = 128

    process_area = ProcessArea(
        coordinates=process_area_coordinates,
        tile_size=tile_size,
    )

    assert id(process_area._coordinates) != id(process_area_coordinates)
    assert id(process_area.coordinates) != id(process_area._coordinates)


def test_process_area_setters(
    process_area: ProcessArea,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        process_area.coordinates = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        process_area.tile_size = None


def test_process_area_serializability(
    process_area: ProcessArea,
) -> None:
    serialized_process_area = pickle.dumps(process_area)
    deserialized_process_area = pickle.loads(serialized_process_area)  # noqa: S301

    assert process_area == deserialized_process_area


@pytest.mark.parametrize(('process_area', 'expected'), data_test_process_area_area)
def test_process_area_area(
    process_area: ProcessArea,
    expected: int,
) -> None:
    assert process_area.area == expected


@pytest.mark.parametrize(
    (
        'bounding_box',
        'tile_size',
        'quantize',
        'expected',
    ),
    data_test_process_area_from_bounding_box,
)
def test_process_area_from_bounding_box(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    quantize: bool,
    expected: ProcessArea,
) -> None:
    process_area = ProcessArea.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )

    assert process_area == expected


@pytest.mark.parametrize(('tile_size', 'message'), data_test_process_area_from_bounding_box_exceptions)
def test_process_area_from_bounding_box_exceptions(
    tile_size: TileSize,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    quantize = True

    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea.from_bounding_box(
            bounding_box=bounding_box,
            tile_size=tile_size,
            quantize=quantize,
        )


def test_process_area_from_bounding_box_defaults() -> None:
    signature = inspect.signature(ProcessArea.from_bounding_box)
    quantize = signature.parameters['quantize'].default

    expected_quantize = True

    assert quantize is expected_quantize


@pytest.mark.parametrize(('gdf', 'tile_size', 'quantize', 'expected'), data_test_process_area_from_gdf)
def test_process_area_from_gdf(
    gdf: gpd.GeoDataFrame,
    tile_size: TileSize,
    quantize: bool,
    expected: ProcessArea,
) -> None:
    process_area = ProcessArea.from_gdf(
        gdf=gdf,
        tile_size=tile_size,
        quantize=quantize,
    )

    assert process_area == expected


@pytest.mark.parametrize(('gdf', 'tile_size', 'message'), data_test_process_area_from_gdf_exceptions)
def test_process_area_from_gdf_exceptions(
    gdf: gpd.GeoDataFrame,
    tile_size: TileSize,
    message: str,
) -> None:
    quantize = True

    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea.from_gdf(
            gdf=gdf,
            tile_size=tile_size,
            quantize=quantize,
        )


def test_process_area_from_gdf_defaults() -> None:
    signature = inspect.signature(ProcessArea.from_gdf)
    quantize = signature.parameters['quantize'].default

    expected_quantize = True

    assert quantize is expected_quantize


@pytest.mark.parametrize(('json_string', 'expected'), data_test_process_area_from_json)
def test_process_area_from_json(
    json_string: str,
    expected: ProcessArea,
) -> None:
    process_area = ProcessArea.from_json(json_string=json_string)

    assert process_area == expected


@pytest.mark.parametrize(('json_string', 'message'), data_test_process_area_from_json_exceptions)
def test_process_area_from_json_exceptions(
    json_string: str,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea.from_json(json_string=json_string)


@pytest.mark.parametrize(('process_areas', 'expected'), data_test_process_area_from_process_areas)
def test_process_area_from_process_areas(
    process_areas: list[ProcessArea],
    expected: ProcessArea,
) -> None:
    process_area = ProcessArea.from_process_areas(process_areas=process_areas)

    assert process_area == expected


@pytest.mark.parametrize(('process_areas', 'message'), data_test_process_area_from_process_areas_exceptions)
def test_process_area_from_process_areas_exceptions(
    process_areas: list[ProcessArea],
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = ProcessArea.from_process_areas(process_areas=process_areas)


@pytest.mark.skip(reason='Not implemented')
def test_process_area_from_config() -> None:
    pass


@pytest.mark.parametrize(('other', 'expected'), data_test_process_area_eq)
def test_process_area_eq(
    other: object,
    expected: bool,
    process_area: ProcessArea,
) -> None:
    equals = process_area == other

    assert equals is expected


def test_process_area_len(
    process_area: ProcessArea,
) -> None:
    expected = 4

    assert len(process_area) == expected


@pytest.mark.parametrize(('process_area', 'expected'), data_test_process_area_bool)
def test_process_area_bool(
    process_area: ProcessArea,
    expected: bool,
) -> None:
    assert bool(process_area) is expected


@pytest.mark.parametrize(('coordinates', 'expected'), data_test_process_area_contains)
def test_process_area_contains(
    coordinates: Coordinates,
    expected: bool,
    process_area: ProcessArea,
) -> None:
    contains = coordinates in process_area

    assert contains is expected


@pytest.mark.parametrize(('index', 'expected'), data_test_process_area_getitem)
def test_process_area_getitem(
    index: int,
    expected: Coordinates,
    process_area: ProcessArea,
) -> None:
    coordinates = process_area[index]

    assert coordinates == expected


@pytest.mark.parametrize(('index', 'expected'), data_test_process_area_getitem_slice)
def test_process_area_getitem_slice(
    index: slice,
    expected: ProcessArea,
    process_area: ProcessArea,
) -> None:
    process_area = process_area[index]

    assert process_area == expected


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


@pytest.mark.parametrize(('other', 'expected'), data_test_process_area_add)
def test_process_area_add(
    other: ProcessArea,
    expected: ProcessArea,
    process_area: ProcessArea,
) -> None:
    process_area = process_area + other

    assert process_area == expected


@pytest.mark.parametrize(('other', 'message'), data_test_process_area_add_exceptions)
def test_process_area_add_exceptions(
    other: ProcessArea,
    message: str,
    process_area: ProcessArea,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = process_area + other


@pytest.mark.parametrize(('other', 'expected'), data_test_process_area_sub)
def test_process_area_sub(
    other: ProcessArea,
    expected: ProcessArea,
    process_area: ProcessArea,
) -> None:
    process_area = process_area - other

    assert process_area == expected


@pytest.mark.parametrize(('other', 'message'), data_test_process_area_sub_exceptions)
def test_process_area_sub_exceptions(
    other: ProcessArea,
    message: str,
    process_area: ProcessArea,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = process_area - other


@pytest.mark.parametrize(('other', 'expected'), data_test_process_area_and)
def test_process_area_and(
    other: ProcessArea,
    expected: ProcessArea,
    process_area: ProcessArea,
) -> None:
    process_area = process_area & other

    assert process_area == expected


@pytest.mark.parametrize(('other', 'message'), data_test_process_area_and_exceptions)
def test_process_area_and_exceptions(
    other: ProcessArea,
    message: str,
    process_area: ProcessArea,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = process_area & other


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_append)
def test_process_area_append(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    process_area_ = process_area.append(
        coordinates=coordinates,
        inplace=False,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected
    assert id(process_area_) != id(process_area)
    assert id(process_area_.coordinates) != id(process_area.coordinates)


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_append_inplace)
def test_process_area_append_inplace(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    process_area.append(
        coordinates=coordinates,
        inplace=True,
    )

    assert process_area == expected


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_append_inplace_return)
def test_process_area_append_inplace_return(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    process_area_ = process_area.append(
        coordinates=coordinates,
        inplace=True,
    )

    assert process_area == expected
    assert process_area_ == expected
    assert id(process_area_) == id(process_area)
    assert id(process_area_.coordinates) != id(process_area.coordinates)


def test_process_area_append_defaults() -> None:
    signature = inspect.signature(ProcessArea.append)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('process_area', 'num_chunks', 'expected'), data_test_process_area_chunk)
def test_process_area_chunk(
    process_area: ProcessArea,
    num_chunks: int,
    expected: list[ProcessArea],
) -> None:
    chunks = process_area.chunk(num_chunks=num_chunks)

    assert chunks == expected


@pytest.mark.parametrize(('num_chunks', 'message'), data_test_process_area_chunk_exceptions)
def test_process_area_chunk_exceptions(
    num_chunks: int,
    message: str,
    process_area: ProcessArea,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = process_area.chunk(num_chunks=num_chunks)


def test_process_area_filter(
    process_area: ProcessArea,
    process_area_coordinates: CoordinatesSet,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = process_area_coordinates

    process_area_ = process_area.filter(
        coordinates_filter=coordinates_filter,
        inplace=False,
    )

    expected_coordinates = process_area_coordinates
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected
    assert id(process_area_) != id(process_area)
    coordinates_filter.assert_called_once()


def test_process_area_filter_inplace(
    process_area: ProcessArea,
    process_area_coordinates: CoordinatesSet,
) -> None:
    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = process_area_coordinates

    process_area.filter(
        coordinates_filter=coordinates_filter,
        inplace=True,
    )

    expected_coordinates = process_area_coordinates
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected
    coordinates_filter.assert_called_once()


def test_process_area_filter_inplace_return(
    process_area: ProcessArea,
    process_area_coordinates: CoordinatesSet,
) -> None:
    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = process_area_coordinates

    process_area_ = process_area.filter(
        coordinates_filter=coordinates_filter,
        inplace=True,
    )

    expected_coordinates = process_area_coordinates
    expected_tile_size = 128
    expected = ProcessArea(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert process_area == expected
    assert process_area_ == expected
    assert id(process_area_) == id(process_area)
    coordinates_filter.assert_called_once()


def test_process_area_filter_defaults() -> None:
    signature = inspect.signature(ProcessArea.filter)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_remove)
def test_process_area_remove(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    copied_process_area = copy.deepcopy(process_area)

    process_area_ = process_area.remove(
        coordinates=coordinates,
        inplace=False,
    )

    assert process_area == copied_process_area
    assert process_area_ == expected
    assert id(process_area_) != id(process_area)
    assert id(process_area_.coordinates) != id(process_area.coordinates)


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_remove_inplace)
def test_process_area_remove_inplace(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    process_area.remove(
        coordinates=coordinates,
        inplace=True,
    )

    assert process_area == expected


@pytest.mark.parametrize(('process_area', 'coordinates', 'expected'), data_test_process_area_remove_inplace_return)
def test_process_area_remove_inplace_return(
    process_area: ProcessArea,
    coordinates: Coordinates | CoordinatesSet,
    expected: ProcessArea,
) -> None:
    process_area_ = process_area.remove(
        coordinates=coordinates,
        inplace=True,
    )

    assert process_area == expected
    assert process_area_ == expected
    assert id(process_area_) == id(process_area)
    assert id(process_area_.coordinates) != id(process_area.coordinates)


def test_process_area_remove_defaults() -> None:
    signature = inspect.signature(ProcessArea.remove)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


def test_process_area_to_gdf(
    process_area: ProcessArea,
) -> None:
    epsg_code = 25832

    gdf = process_area.to_gdf(epsg_code=epsg_code)

    expected_geometry = [
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ]
    expected_epsg_code = 'EPSG:25832'
    expected = gpd.GeoDataFrame(
        geometry=expected_geometry,
        crs=expected_epsg_code,
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
