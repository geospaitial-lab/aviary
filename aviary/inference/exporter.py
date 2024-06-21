from typing import Protocol
from pathlib import Path

import numpy as np
import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.inference.exporter import segmentation_exporter

# noinspection PyProtectedMember
from aviary._utils.types import (
    CoordinatesSet,
    EPSGCode,
    GroundSamplingDistance,
    SegmentationExporterMode,
    TileSize,
)


class Exporter(Protocol):
    """Protocol for exporters

    Exporters are callables that export predictions.
    The exporter is used by the pipeline to export the batched output of the model's inference.

    Currently implemented exporters:
        - SegmentationExporter: Exports segmentation predictions
    """

    def __call__(
        self,
        preds: npt.NDArray[np.uint8],
        coordinates: CoordinatesSet,
    ) -> None:
        """Exports the predictions.

        Parameters:
            preds: batched predictions
            coordinates: coordinates (x_min, y_min) of each tile
        """
        ...


class SegmentationExporter:
    """Exporter for segmentation predictions

    Implements the Exporter protocol.

    The predictions (i.e. raster data) are transformed to geospatial data (i.e. vector data).
    The resulting geodataframe contains the geometry of the polygons and their class that is stored
    in the field `field_name` as the pixel value of the prediction.

    Available modes:
        - `FEATHER`: For each processed tile, the segmentation exporter creates a subdirectory named `{x_min}_{y_min}`
          (if the tile contains any polygons, it exports the geodataframe as a feather file
          named `{x_min}_{y_min}.feather`)
        - `GPKG`: The segmentation exporter creates a geopackage named `output.gpkg`
    """
    _GPKG_NAME = 'output.gpkg'
    _IGNORE_BACKGROUND_CLASS = True

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        epsg_code: EPSGCode,
        field_name: str = 'class',
        mode: SegmentationExporterMode = SegmentationExporterMode.GPKG,
        num_workers: int = 1,
    ) -> None:
        """
        Parameters:
            path: path to the output directory
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            epsg_code: EPSG code
            field_name: name of the field in the geodataframe
            mode: segmentation exporter mode (`FEATHER` or `GPKG`)
            num_workers: number of workers
        """
        self.path = path
        self.tile_size = tile_size
        self.ground_sampling_distance = ground_sampling_distance
        self.epsg_code = epsg_code
        self.field_name = field_name
        self.mode = mode
        self.num_workers = num_workers

    def __call__(
        self,
        preds: npt.NDArray[np.uint8],
        coordinates: CoordinatesSet,
    ) -> None:
        """Exports the predictions.

        Parameters:
            preds: batched predictions
            coordinates: coordinates (x_min, y_min) of each tile

        Raises:
            AviaryUserError: Invalid segmentation exporter mode
        """
        segmentation_exporter(
            preds=preds,
            coordinates=coordinates,
            path=self.path,
            tile_size=self.tile_size,
            ground_sampling_distance=self.ground_sampling_distance,
            epsg_code=self.epsg_code,
            field_name=self.field_name,
            ignore_background_class=self._IGNORE_BACKGROUND_CLASS,
            gpkg_name=self._GPKG_NAME,
            mode=self.mode,
            num_workers=self.num_workers,
        )