from pathlib import Path

import dask
import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.features

# noinspection PyProtectedMember
from aviary._utils.types import (
    Coordinate,
    CoordinatesSet,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)


def segmentation_exporter(
    preds: npt.NDArray[np.uint8],
    coordinates: CoordinatesSet,
    path: Path,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    epsg_code: EPSGCode,
    field_name: str = 'class',
    ignore_background_class: bool = True,
    num_workers: int = 1,
) -> None:
    """Vectorizes the predictions and exports the geodataframe to the output directory.

    Parameters:
        preds: batched predictions
        coordinates: coordinates (x_min, y_min) of each tile
        path: path to the output directory
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        epsg_code: EPSG code
        field_name: name of the field in the geodataframe
        ignore_background_class: if True, the background class is not additionally vectorized as a polygon of class 0
        num_workers: number of workers
    """
    tasks = [
        _segmentation_exporter_task(
            preds=preds_element,
            x_min=coordinates_element[0],
            y_min=coordinates_element[1],
            path=path,
            tile_size=tile_size,
            ground_sampling_distance=ground_sampling_distance,
            epsg_code=epsg_code,
            field_name=field_name,
            ignore_background_class=ignore_background_class,
        )
        for preds_element, coordinates_element
        in zip(preds, coordinates)
    ]
    dask.compute(tasks, num_workers=num_workers)


@dask.delayed
def _segmentation_exporter_task(
    preds: npt.NDArray[np.uint8],
    x_min: Coordinate,
    y_min: Coordinate,
    path: Path,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    epsg_code: EPSGCode,
    field_name: str = 'class',
    ignore_background_class: bool = True,
) -> None:
    """Vectorizes the predictions and exports the geodataframe to the output directory.

    Notes:
        - This function is called concurrently by the `segmentation_exporter` function

    Parameters:
        preds: predictions
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        path: path to the output directory
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        epsg_code: EPSG code
        field_name: name of the field in the geodataframe
        ignore_background_class: if True, the background class is not additionally vectorized as a polygon of class 0
    """
    gdf = _vectorize_preds(
        preds=preds,
        x_min=x_min,
        y_min=y_min,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        ignore_background_class=ignore_background_class,
    )
    _export_gdf(
        gdf=gdf,
        x_min=x_min,
        y_min=y_min,
        path=path,
    )


def _export_gdf(
    gdf: gpd.GeoDataFrame | None,
    x_min: Coordinate,
    y_min: Coordinate,
    path: Path,
) -> None:
    """Exports the geodataframe to the output directory.

    Parameters:
        gdf: geodataframe of the vectorized predictions
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        path: path to the output directory
    """
    processed_dir_path = path / f'{x_min}_{y_min}'
    processed_dir_path.mkdir(exist_ok=True)

    for path in processed_dir_path.iterdir():
        path.unlink()

    if gdf is not None:
        gdf_path = processed_dir_path / f'{x_min}_{y_min}.feather'
        gdf.to_feather(gdf_path)


def _vectorize_preds(
    preds: npt.NDArray[np.uint8],
    x_min: Coordinate,
    y_min: Coordinate,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    epsg_code: EPSGCode,
    field_name: str = 'class',
    ignore_background_class: bool = True,
) -> gpd.GeoDataFrame | None:
    """Vectorizes the predictions.

    Parameters:
        preds: predictions
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        epsg_code: EPSG code
        field_name: name of the field in the geodataframe
        ignore_background_class: if True, the background class is not additionally vectorized as a polygon of class 0

    Returns:
        vectorized predictions
    """
    y_max = y_min + tile_size
    transform = rio.transform.from_origin(
        west=x_min,
        north=y_max,
        xsize=ground_sampling_distance,
        ysize=ground_sampling_distance,
    )
    features = [
        {'properties': {field_name: int(value)},
         'geometry': polygon}
        for polygon, value
        in rio.features.shapes(
            source=preds,
            transform=transform,
        )
        if not ignore_background_class or int(value) != 0
    ]

    if features:
        gdf = gpd.GeoDataFrame.from_features(
            features=features,
            crs=f'EPSG:{epsg_code}',
        )
        gdf[field_name] = gdf[field_name].astype(np.uint8)
        return gdf
    return None
