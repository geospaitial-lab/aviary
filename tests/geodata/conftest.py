from unittest.mock import MagicMock

import geopandas as gpd
import pytest

from aviary.geodata.geodata_postprocessor import (
    ClipPostprocessor,
    CompositePostprocessor,
    FieldNamePostprocessor,
    FillPostprocessor,
    GeodataPostprocessor,
    SievePostprocessor,
    SimplifyPostprocessor,
    ValuePostprocessor,
)


@pytest.fixture(scope='session')
def clip_postprocessor() -> ClipPostprocessor:
    geometry = []
    epsg_code = 25832
    mask = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    return ClipPostprocessor(
        mask=mask,
    )


@pytest.fixture(scope='session')
def composite_postprocessor() -> CompositePostprocessor:
    geodata_postprocessors = [
        MagicMock(spec=GeodataPostprocessor),
        MagicMock(spec=GeodataPostprocessor),
        MagicMock(spec=GeodataPostprocessor),
    ]
    return CompositePostprocessor(
        geodata_postprocessors=geodata_postprocessors,
    )


@pytest.fixture(scope='session')
def field_name_postprocessor() -> FieldNamePostprocessor:
    mapping = {'old field name': 'new field name'}
    return FieldNamePostprocessor(
        mapping=mapping,
    )


@pytest.fixture(scope='session')
def fill_postprocessor() -> FillPostprocessor:
    max_area = 1.
    return FillPostprocessor(
        max_area=max_area,
    )


@pytest.fixture(scope='session')
def sieve_postprocessor() -> SievePostprocessor:
    min_area = 1.
    return SievePostprocessor(
        min_area=min_area,
    )


@pytest.fixture(scope='session')
def simplify_postprocessor() -> SimplifyPostprocessor:
    tolerance = 1.
    return SimplifyPostprocessor(
        tolerance=tolerance,
    )


@pytest.fixture(scope='session')
def value_postprocessor() -> ValuePostprocessor:
    mapping = {'old value': 'new value'}
    field_name = 'field name'
    return ValuePostprocessor(
        mapping=mapping,
        field_name=field_name,
    )
