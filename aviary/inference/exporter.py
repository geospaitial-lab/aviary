from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING, Protocol

import pydantic

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.inference.exporter import segmentation_exporter

# noinspection PyProtectedMember
from aviary._utils.mixins import FromConfigMixin
from aviary.core.type_aliases import (  # noqa: TC001
    CoordinatesSet,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)


class Exporter(Protocol):
    """Protocol for exporters

    Exporters are callables that export predictions.
    The exporter is used by the pipeline to export the batched output of the model's inference.

    Currently implemented exporters:
        - `SegmentationExporter`: Exports segmentation predictions
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


class SegmentationExporter(FromConfigMixin):
    """Exporter for segmentation predictions

    Implements the `Exporter` protocol.

    The predictions (i.e. raster data) are transformed to geospatial data (i.e. vector data).
    The resulting geodataframe contains the geometry of the polygons and their class that is stored
    in the field `field_name` as the pixel value of the prediction.
    The segmentation exporter creates a geopackage named `output.gpkg` and exports the geodataframe
    of each tile dynamically.
    The coordinates of the bottom left corner of the processed tiles and the tile size are exported dynamically
    to a JSON file named `processed_coordinates.json`.

    Notes:
        - The segmentation exporter uses multiple threads to vectorize and export the predictions
    """
    _GPKG_NAME = 'output.gpkg'
    _JSON_NAME = 'processed_coordinates.json'
    _IGNORE_BACKGROUND_CLASS = True

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        epsg_code: EPSGCode,
        field_name: str = 'class',
        num_workers: int = 4,
    ) -> None:
        """
        Parameters:
            path: path to the output directory
            tile_size: tile size in meters
            ground_sampling_distance: ground sampling distance in meters
            epsg_code: EPSG code
            field_name: name of the field in the geodataframe
            num_workers: number of workers
        """
        self.path = path
        self.tile_size = tile_size
        self.ground_sampling_distance = ground_sampling_distance
        self.epsg_code = epsg_code
        self.field_name = field_name
        self.num_workers = num_workers

    @classmethod
    def from_config(
        cls,
        config: SegmentationExporterConfig,
    ) -> SegmentationExporter:
        """Creates a segmentation exporter from the configuration.

        Parameters:
            config: configuration

        Returns:
            segmentation exporter
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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
            json_name=self._JSON_NAME,
            num_workers=self.num_workers,
        )


class SegmentationExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SegmentationExporter`

    Attributes:
        path: path to the output directory
        tile_size: tile size in meters
        ground_sampling_distance: ground sampling distance in meters
        epsg_code: EPSG code
        field_name: name of the field in the geodataframe
        num_workers: number of workers
    """
    path: Path
    tile_size: TileSize
    ground_sampling_distance: GroundSamplingDistance
    epsg_code: EPSGCode
    field_name: str = 'class'
    num_workers: int = 4
