import multiprocessing
from pathlib import Path

import dask
import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio as rio
import rasterio.features

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError

# noinspection PyProtectedMember
from aviary._utils.types import (
    Coordinate,
    CoordinatesSet,
    EPSGCode,
    GroundSamplingDistance,
    SegmentationExporterMode,
    TileSize,
)

_lock = multiprocessing.Lock()


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
    mode: SegmentationExporterMode = SegmentationExporterMode.GPKG,
    num_workers: int = 1,
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
        gpkg_name: name of the geopackage (only used if `mode` is `GPKG`)
        mode: segmentation exporter mode (`FEATHER` or `GPKG`)
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
            gpkg_name=gpkg_name,
            mode=mode,
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
    gpkg_name: str = 'output.gpkg',
    mode: SegmentationExporterMode = SegmentationExporterMode.GPKG,
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
        gpkg_name: name of the geopackage (only used if `mode` is `GPKG`)
        mode: segmentation exporter mode (`FEATHER` or `GPKG`)
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
        x_min=x_min,
        y_min=y_min,
        gpkg_name=gpkg_name,
        mode=mode,
    )


def _export_gdf(
    gdf: gpd.GeoDataFrame | None,
    path: Path,
    x_min: Coordinate,
    y_min: Coordinate,
    gpkg_name: str = 'output.gpkg',
    mode: SegmentationExporterMode = SegmentationExporterMode.GPKG,
) -> None:
    """Exports the geodataframe.

    Parameters:
        gdf: geodataframe of the vectorized predictions
        path: path to the output directory
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        gpkg_name: name of the geopackage (only used if `mode` is `GPKG`)
        mode: segmentation exporter mode (`FEATHER` or `GPKG`)

    Raises:
        AviaryUserError: Invalid segmentation exporter mode
    """
    if mode == SegmentationExporterMode.FEATHER:
        _export_gdf_feather(
            gdf=gdf,
            path=path,
            x_min=x_min,
            y_min=y_min,
        )
        return

    if mode == SegmentationExporterMode.GPKG:
        _export_gdf_gpkg(
            gdf=gdf,
            path=path,
            gpkg_name=gpkg_name,
        )
        return

    message = 'Invalid segmentation exporter mode!'
    raise AviaryUserError(message)


def _export_gdf_feather(
    gdf: gpd.GeoDataFrame | None,
    path: Path,
    x_min: Coordinate,
    y_min: Coordinate,
) -> None:
    """Exports the geodataframe as a feather file.

    Parameters:
        gdf: geodataframe of the vectorized predictions
        path: path to the output directory
        x_min: minimum x coordinate
        y_min: minimum y coordinate
    """
    subdir_path = path / f'{x_min}_{y_min}'
    subdir_path.mkdir(exist_ok=True)

    for path in subdir_path.iterdir():
        path.unlink()

    if gdf is None:
        return

    gdf_path = subdir_path / f'{x_min}_{y_min}.feather'
    gdf.to_feather(gdf_path)


def _export_gdf_gpkg(
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
    with _lock:
        try:
            gdf.to_file(gdf_path, driver='GPKG', mode='a')
        except OSError:
            gdf.to_file(gdf_path, driver='GPKG')


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
