from unittest.mock import MagicMock, patch

import geopandas as gpd
import geopandas.testing

import aviary.geodata.geodata_postprocessor
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


def test_globals() -> None:
    class_names = [
        'ClipPostprocessor',
        'FieldNamePostprocessor',
        'FillPostprocessor',
        'SievePostprocessor',
        'SimplifyPostprocessor',
        'ValuePostprocessor',
    ]

    for class_name in class_names:
        assert hasattr(aviary.geodata.geodata_postprocessor, class_name)


def test_clip_postprocessor_init() -> None:
    geometry = []
    epsg_code = 25832
    mask = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    clip_postprocessor = ClipPostprocessor(
        mask=mask,
    )

    gpd.testing.assert_geodataframe_equal(clip_postprocessor.mask, mask)


@patch('aviary.geodata.geodata_postprocessor.clip_postprocessor')
def test_clip_postprocessor_call(
    mocked_clip_postprocessor: MagicMock,
    clip_postprocessor: ClipPostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_clip_postprocessor.return_value = expected
    postprocessed_geodata = clip_postprocessor(
        gdf=gdf,
    )

    mocked_clip_postprocessor.assert_called_once_with(
        gdf=gdf,
        mask=clip_postprocessor.mask,
    )
    assert postprocessed_geodata == expected


def test_composite_postprocessor_init() -> None:
    geodata_postprocessors = [
        MagicMock(spec=GeodataPostprocessor),
        MagicMock(spec=GeodataPostprocessor),
        MagicMock(spec=GeodataPostprocessor),
    ]
    composite_postprocessor = CompositePostprocessor(
        geodata_postprocessors=geodata_postprocessors,
    )

    assert composite_postprocessor.geodata_postprocessors == geodata_postprocessors


@patch('aviary.geodata.geodata_postprocessor.composite_postprocessor')
def test_composite_postprocessor_call(
    mocked_composite_postprocessor: MagicMock,
    composite_postprocessor: CompositePostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_composite_postprocessor.return_value = expected
    postprocessed_geodata = composite_postprocessor(
        gdf=gdf,
    )

    mocked_composite_postprocessor.assert_called_once_with(
        gdf=gdf,
        geodata_postprocessors=composite_postprocessor.geodata_postprocessors,
    )
    assert postprocessed_geodata == expected


def test_field_name_postprocessor_init() -> None:
    mapping = {'old field name': 'new field name'}
    field_name_postprocessor = FieldNamePostprocessor(
        mapping=mapping,
    )

    assert field_name_postprocessor.mapping == mapping


@patch('aviary.geodata.geodata_postprocessor.field_name_postprocessor')
def test_field_name_postprocessor_call(
    mocked_field_name_postprocessor: MagicMock,
    field_name_postprocessor: FieldNamePostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_field_name_postprocessor.return_value = expected
    postprocessed_geodata = field_name_postprocessor(
        gdf=gdf,
    )

    mocked_field_name_postprocessor.assert_called_once_with(
        gdf=gdf,
        mapping=field_name_postprocessor.mapping,
    )
    assert postprocessed_geodata == expected


def test_fill_postprocessor_init() -> None:
    max_area = 1.
    fill_postprocessor = FillPostprocessor(
        max_area=max_area,
    )

    assert fill_postprocessor.max_area == max_area


@patch('aviary.geodata.geodata_postprocessor.fill_postprocessor')
def test_fill_postprocessor_call(
    mocked_fill_postprocessor: MagicMock,
    fill_postprocessor: FillPostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_fill_postprocessor.return_value = expected
    postprocessed_geodata = fill_postprocessor(
        gdf=gdf,
    )

    mocked_fill_postprocessor.assert_called_once_with(
        gdf=gdf,
        max_area=fill_postprocessor.max_area,
    )
    assert postprocessed_geodata == expected


def test_sieve_postprocessor_init() -> None:
    min_area = 1.
    sieve_postprocessor = SievePostprocessor(
        min_area=min_area,
    )

    assert sieve_postprocessor.min_area == min_area


@patch('aviary.geodata.geodata_postprocessor.sieve_postprocessor')
def test_sieve_postprocessor_call(
    mocked_sieve_postprocessor: MagicMock,
    sieve_postprocessor: SievePostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_sieve_postprocessor.return_value = expected
    postprocessed_geodata = sieve_postprocessor(
        gdf=gdf,
    )

    mocked_sieve_postprocessor.assert_called_once_with(
        gdf=gdf,
        min_area=sieve_postprocessor.min_area,
    )
    assert postprocessed_geodata == expected


def test_simplify_postprocessor_init() -> None:
    tolerance = 1.
    simplify_postprocessor = SimplifyPostprocessor(
        tolerance=tolerance,
    )

    assert simplify_postprocessor.tolerance == tolerance


@patch('aviary.geodata.geodata_postprocessor.simplify_postprocessor')
def test_simplify_postprocessor_call(
    mocked_simplify_postprocessor: MagicMock,
    simplify_postprocessor: SimplifyPostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_simplify_postprocessor.return_value = expected
    postprocessed_geodata = simplify_postprocessor(
        gdf=gdf,
    )

    mocked_simplify_postprocessor.assert_called_once_with(
        gdf=gdf,
        tolerance=simplify_postprocessor.tolerance,
    )
    assert postprocessed_geodata == expected


def test_value_postprocessor_init() -> None:
    mapping = {'old value': 'new value'}
    value_postprocessor = ValuePostprocessor(
        mapping=mapping,
    )

    assert value_postprocessor.mapping == mapping


@patch('aviary.geodata.geodata_postprocessor.value_postprocessor')
def test_value_postprocessor_call(
    mocked_value_postprocessor: MagicMock,
    value_postprocessor: ValuePostprocessor,
) -> None:
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    expected = 'expected'
    mocked_value_postprocessor.return_value = expected
    postprocessed_geodata = value_postprocessor(
        gdf=gdf,
    )

    mocked_value_postprocessor.assert_called_once_with(
        gdf=gdf,
        mapping=value_postprocessor.mapping,
        field_name=value_postprocessor.field_name,
    )
    assert postprocessed_geodata == expected
