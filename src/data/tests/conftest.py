import pytest

from src.data.grid_generator import GridGenerator


@pytest.fixture(scope='session')
def grid_generator() -> GridGenerator:
    bounding_box = (-128, -128, 128, 128)
    epsg_code = 25832
    return GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )
