from pathlib import Path

import numpy as np
import numpy.typing as npt

from .._functional.geodata.vectorizer import vectorizer
from ..utils.types import (
    Coordinates,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)


class Vectorizer:
    """Vectorizer

    A vectorizer is a callable that transforms predictions of the model (i.e. raster data) to
    geospatial data (i.e. vector data).
    The vectorizer is used by the pipeline to vectorize the batched predictions and export the geodataframe of
    the polygons as a memory and time efficient feather file to the output directory.
    The geodataframe contains the geometry of the polygons and their class that is stored in the field `field_name`
    as the pixel value of the prediction.

    For each processed tile, the vectorizer creates a subdirectory named `{x_min}_{y_min}`.
    If the tile contains any polygons, it exports the geodataframe as a feather file named `{x_min}_{y_min}.feather`.
    """
    _IGNORE_BACKGROUND_CLASS = True

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        epsg_code: EPSGCode,
        field_name: str = 'class',
        num_workers: int = 1,
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

    def __call__(
        self,
        preds: npt.NDArray[np.uint8],
        coordinates: Coordinates,
    ) -> None:
        """Vectorizes the predictions and exports the geodataframe to the output directory.

        Parameters:
            preds: batched predictions
            coordinates: coordinates (x_min, y_min) of each tile
        """
        vectorizer(
            preds=preds,
            coordinates=coordinates,
            path=self.path,
            tile_size=self.tile_size,
            ground_sampling_distance=self.ground_sampling_distance,
            epsg_code=self.epsg_code,
            field_name=self.field_name,
            ignore_background_class=self._IGNORE_BACKGROUND_CLASS,
            num_workers=self.num_workers,
        )
