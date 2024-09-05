import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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
    ProcessArea,
    TileSize,
)

_lock_gpkg = threading.Lock()
_lock_json = threading.Lock()


def segmentation_exporter(
    preds: npt.NDArray[np.uint8],
    coordinates: CoordinatesSet,
    path: Path,
    tile_size: TileSize,
    ground_sampling_distance: GroundSamplingDistance,
    epsg_code: EPSGCode,
    field_name: str = 'class',
    ignore_background_class: bool = True,
    gpkg_name: str = 'output.gpkg',
    json_name: str = 'processed_coordinates.json',
    num_workers: int = 4,
) -> None:
    """Exports the predictions.

    Parameters:
        preds: batched predictions
        coordinates: coordinates (x_min, y_min) of each tile
        path: path to the output directory
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        epsg_code: EPSG code
        field_name: name of the field in the geodataframe
        ignore_background_class: if True, the background class is not additionally vectorized as a polygon of class 0
        gpkg_name: name of the geopackage
        json_name: name of the JSON file containing the coordinates of the processed tiles
        num_workers: number of workers
    """
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for preds_item, coordinates_item in zip(preds, coordinates, strict=True):
            executor.submit(
                _segmentation_exporter_task,
                preds=preds_item,
                x_min=coordinates_item[0],
                y_min=coordinates_item[1],
                path=path,
                tile_size=tile_size,
                ground_sampling_distance=ground_sampling_distance,
                epsg_code=epsg_code,
                field_name=field_name,
                ignore_background_class=ignore_background_class,
                gpkg_name=gpkg_name,
                json_name=json_name,
            )


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
    gpkg_name: str = 'output.gpkg',
    json_name: str = 'processed_coordinates.json',
) -> None:
    """Exports the predictions.

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
        gpkg_name: name of the geopackage
        json_name: name of the JSON file containing the coordinates of the processed tiles
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
        path=path,
        gpkg_name=gpkg_name,
    )
    _export_coordinates_json(
        x_min=x_min,
        y_min=y_min,
        path=path,
        json_name=json_name,
    )


def _export_gdf(
    gdf: gpd.GeoDataFrame | None,
    path: Path,
    gpkg_name: str = 'output.gpkg',
) -> None:
    """Exports the geodataframe as a geopackage.

    Parameters:
        gdf: geodataframe of the vectorized predictions
        path: path to the output directory
        gpkg_name: name of the geopackage
    """
    if gdf is None:
        return

    gdf_path = path / gpkg_name

    with _lock_gpkg:
        try:
            gdf.to_file(gdf_path, driver='GPKG', mode='a')
        except OSError:
            gdf.to_file(gdf_path, driver='GPKG')


def _export_coordinates_json(
    x_min: Coordinate,
    y_min: Coordinate,
    path: Path,
    json_name: str = 'processed_coordinates.json',
) -> None:
    """Exports the coordinates of the processed tiles as a JSON file.

    Parameters:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        path: path to the output directory
        json_name: name of the JSON file containing the coordinates of the processed tiles
    """
    coordinates = (x_min, y_min)
    json_path = path / json_name

    with _lock_json:
        try:
            with json_path.open() as file:
                json_string = json.load(file)
            process_area = ProcessArea.from_json(json_string)
        except FileNotFoundError:
            process_area = ProcessArea()

        process_area = process_area.append(coordinates)
        json_string = process_area.to_json()

        with json_path.open('w') as file:
            json.dump(json_string, file)


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
