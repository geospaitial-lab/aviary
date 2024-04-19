import pytest

from src.utils.tests.data.data_test_validators import (
    data_test_validate_bounding_box_type_error,
    data_test_validate_bounding_box_value_error,
    data_test_validate_epsg_code_type_error,
    data_test_validate_epsg_code_value_error,
    data_test_validate_tile_size_type_error,
    data_test_validate_tile_size_value_error,
)
from src.utils.validators import (
    raise_type_error,
    validate_bounding_box,
    validate_epsg_code,
    validate_tile_size,
)


def test_raise_type_error() -> None:
    message = (
        'Invalid type for param. '
        'Expected <class \'int\'>, but got <class \'str\'>.'
    )
    with pytest.raises(TypeError, match=message):
        raise_type_error(
            param_name='param',
            expected_type=int,
            actual_type=str,
        )


def test_validate_bounding_box() -> None:
    bounding_box = (-128, -128, 128, 128)
    validate_bounding_box(bounding_box)


@pytest.mark.parametrize('bounding_box, message', data_test_validate_bounding_box_type_error)
def test_validate_bounding_box_type_error(
    bounding_box,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        validate_bounding_box(bounding_box)


@pytest.mark.parametrize('bounding_box, message', data_test_validate_bounding_box_value_error)
def test_validate_bounding_box_value_error(
    bounding_box,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_bounding_box(bounding_box)


def test_validate_epsg_code() -> None:
    epsg_code = 25832
    validate_epsg_code(epsg_code)


@pytest.mark.parametrize('epsg_code, message', data_test_validate_epsg_code_type_error)
def test_validate_epsg_code_type_error(
    epsg_code,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        validate_epsg_code(epsg_code)


@pytest.mark.parametrize('epsg_code, message', data_test_validate_epsg_code_value_error)
def test_validate_epsg_code_value_error(
    epsg_code,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_epsg_code(epsg_code)


def test_validate_tile_size() -> None:
    tile_size = 256
    validate_tile_size(tile_size)


@pytest.mark.parametrize('tile_size, message', data_test_validate_tile_size_type_error)
def test_validate_tile_size_type_error(
    tile_size,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        validate_tile_size(tile_size)


@pytest.mark.parametrize('tile_size, message', data_test_validate_tile_size_value_error)
def test_validate_tile_size_value_error(
    tile_size,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_tile_size(tile_size)
