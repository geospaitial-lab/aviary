import geopandas as gpd
import geopandas.testing
import pytest
import shapely.testing
from shapely.geometry import Polygon

from aviary._functional.geodata.geodata_postprocessor import (
    _fill_polygon,
    field_name_postprocessor,
    fill_postprocessor,
    sieve_postprocessor,
    value_postprocessor,
)
from aviary._functional.geodata.tests.data.data_test_geodata_postprocessor import (
    data_test__fill_polygon,
    data_test_field_name_postprocessor,
    data_test_fill_postprocessor,
    data_test_sieve_postprocessor,
    data_test_value_postprocessor,
)


@pytest.mark.skip(reason='Not implemented')
def test_clip_postprocessor() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test_composite_postprocessor() -> None:
    pass


@pytest.mark.parametrize('gdf, mapping, expected', data_test_field_name_postprocessor)
def test_field_name_postprocessor(
    gdf: gpd.GeoDataFrame,
    mapping: dict,
    expected: gpd.GeoDataFrame,
) -> None:
    postprocessed_gdf = field_name_postprocessor(
        gdf=gdf,
        mapping=mapping,
    )

    gpd.testing.assert_geodataframe_equal(postprocessed_gdf, expected)


@pytest.mark.parametrize('gdf, max_area, expected', data_test_fill_postprocessor)
def test_fill_postprocessor(
    gdf: gpd.GeoDataFrame,
    max_area: float,
    expected: gpd.GeoDataFrame,
) -> None:
    postprocessed_gdf = fill_postprocessor(
        gdf=gdf,
        max_area=max_area,
    )

    gpd.testing.assert_geodataframe_equal(postprocessed_gdf, expected)


@pytest.mark.parametrize('polygon, max_area, expected', data_test__fill_polygon)
def test__fill_polygon(
    polygon: Polygon,
    max_area: float,
    expected: Polygon,
) -> None:
    filled_polygon = _fill_polygon(
        polygon=polygon,
        max_area=max_area,
    )

    shapely.testing.assert_geometries_equal(filled_polygon, expected)


@pytest.mark.parametrize('gdf, min_area, expected', data_test_sieve_postprocessor)
def test_sieve_postprocessor(
    gdf: gpd.GeoDataFrame,
    min_area: float,
    expected: gpd.GeoDataFrame,
) -> None:
    postprocessed_gdf = sieve_postprocessor(
        gdf=gdf,
        min_area=min_area,
    )

    gpd.testing.assert_geodataframe_equal(postprocessed_gdf, expected)


@pytest.mark.skip(reason='Not implemented')
def test_simplify_postprocessor() -> None:
    pass


@pytest.mark.parametrize('gdf, mapping, field_name, expected', data_test_value_postprocessor)
def test_value_postprocessor(
    gdf: gpd.GeoDataFrame,
    mapping: dict,
    field_name: str,
    expected: gpd.GeoDataFrame,
) -> None:
    postprocessed_gdf = value_postprocessor(
        gdf=gdf,
        mapping=mapping,
        field_name=field_name,
    )

    gpd.testing.assert_geodataframe_equal(postprocessed_gdf, expected)
