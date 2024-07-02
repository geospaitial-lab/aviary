from __future__ import annotations

import json
from dataclasses import dataclass, fields
from enum import Enum
from math import ceil, floor
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    TypeAlias,
    cast,
)

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pydantic
import rasterio as rio
from shapely.geometry import box

# noinspection PyProtectedMember
from aviary._functional.geodata.coordinates_filter import (
    duplicates_filter,
    geospatial_filter,
    set_filter,
)

# noinspection PyProtectedMember
from aviary._functional.geodata.grid_generator import compute_coordinates
from aviary._utils.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.geodata.coordinates_filter import CoordinatesFilter

BufferSize: TypeAlias = int
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int


@dataclass
class BoundingBox(Iterable[Coordinate]):
    """
    Attributes:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        x_max: maximum x coordinate
        y_max: maximum y coordinate
    """
    x_min: Coordinate
    y_min: Coordinate
    x_max: Coordinate
    y_max: Coordinate

    def __init__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
        x_max: Coordinate,
        y_max: Coordinate,
    ) -> None:
        """
        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate
            x_max: maximum x coordinate
            y_max: maximum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max` or `y_min` >= `y_max`)
        """
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max

        if self._x_min >= self._x_max:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        if self._y_min >= self._y_max:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

    @property
    def x_min(self) -> Coordinate:
        """
        Returns:
            minimum x coordinate
        """
        return self._x_min

    @x_min.setter
    def x_min(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: minimum x coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max`)
        """
        if value >= self._x_max:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        self._x_min = value

    @property
    def y_min(self) -> Coordinate:
        """
        Returns:
            minimum y coordinate
        """
        return self._y_min

    @y_min.setter
    def y_min(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: minimum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`y_min` >= `y_max`)
        """
        if value >= self._y_max:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

        self._y_min = value

    @property
    def x_max(self) -> Coordinate:
        """
        Returns:
            maximum x coordinate
        """
        return self._x_max

    @x_max.setter
    def x_max(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: maximum x coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max`)
        """
        if value <= self._x_min:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        self._x_max = value

    @property
    def y_max(self) -> Coordinate:
        """
        Returns:
            maximum y coordinate
        """
        return self._y_max

    @y_max.setter
    def y_max(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: maximum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`y_min` >= `y_max`)
        """
        if value <= self._y_min:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

        self._y_max = value

    @classmethod
    def from_gdf(
        cls,
        gdf: gpd.GeoDataFrame,
    ) -> BoundingBox:
        """Creates a bounding box from a geodataframe.

        Parameters:
            gdf: geodataframe

        Returns:
            bounding box
        """
        x_min, y_min, x_max, y_max = gdf.total_bounds
        return cls(
            x_min=floor(x_min),
            y_min=floor(y_min),
            x_max=ceil(x_max),
            y_max=ceil(y_max),
        )

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            number of coordinates
        """
        return len(fields(self))

    def __getitem__(
        self,
        index: int,
    ) -> Coordinate:
        """Returns the coordinate given the index.

        Parameters:
            index: index of the coordinate

        Returns:
            coordinate
        """
        field = fields(self)[index]
        return getattr(self, field.name)

    def __iter__(self) -> Iterator[Coordinate]:
        """Iterates over the coordinates.

        Yields:
            coordinate
        """
        for field in fields(self):
            yield getattr(self, field.name)

    def buffer(
        self,
        buffer_size: BufferSize,
        inplace: bool = False,
    ) -> BoundingBox:
        """Buffers the bounding box.

        Parameters:
            buffer_size: buffer size in meters
            inplace: if True, the bounding box is buffered inplace

        Returns:
            buffered bounding box

        Raises:
            AviaryUserError: Invalid buffer size (abs(`buffer_size`) >= half the width or height of the bounding box)
        """
        conditions = [
            buffer_size < 0,
            abs(buffer_size) >= (self._x_max - self._x_min) / 2 or
            abs(buffer_size) >= (self._y_max - self._y_min) / 2,
        ]

        if all(conditions):
            message = (
                'Invalid buffer size! '
                'buffer_size must be less than half the width or height of the bounding box.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - buffer_size
        y_min = self._y_min - buffer_size
        x_max = self._x_max + buffer_size
        y_max = self._y_max + buffer_size

        if inplace:
            self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
            return self
        else:
            return BoundingBox(
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
            )

    def quantize(
        self,
        value: int,
        inplace: bool = False,
    ) -> BoundingBox:
        """Quantizes the coordinates to the specified value.

        Parameters:
            value: value to quantize the coordinates to in meters
            inplace: if True, the bounding box is quantized inplace

        Returns:
            quantized bounding box

        Raises:
            AviaryUserError: Invalid value (`value` <= 0)
        """
        if value <= 0:
            message = (
                'Invalid value! '
                'value must be positive.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - self._x_min % value
        y_min = self._y_min - self._y_min % value
        x_max = self._x_max + (value - self._x_max % value) % value
        y_max = self._y_max + (value - self._y_max % value) % value

        if inplace:
            self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
            return self
        else:
            return BoundingBox(
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
            )

    def to_gdf(
        self,
        epsg_code: EPSGCode,
    ) -> gpd.GeoDataFrame:
        """Converts the bounding box to a geodataframe.

        Parameters:
            epsg_code: EPSG code

        Returns:
            bounding box
        """
        return gpd.GeoDataFrame(
            geometry=[box(self._x_min, self._y_min, self._x_max, self._y_max)],
            crs=f'EPSG:{epsg_code}',
        )


@dataclass
class DataFetcherInfo:
    """
    Attributes:
        bounding_box: bounding box
        dtype: data type of each channel
        epsg_code: EPSG code
        ground_sampling_distance: ground sampling distance in meters
        num_channels: number of channels
    """
    bounding_box: BoundingBox
    dtype: list[DType]
    epsg_code: EPSGCode
    ground_sampling_distance: GroundSamplingDistance
    num_channels: int


class Device(Enum):
    """
    Attributes:
        CPU: CPU device
        CUDA: CUDA device
    """
    CPU = 'cpu'
    CUDA = 'cuda'


class DType(Enum):
    """
    Attributes:
        BOOL: boolean data type
        FLOAT32: 32-bit floating point data type
        UINT8: 8-bit unsigned integer data type
    """
    BOOL = np.bool_
    FLOAT32 = np.float32
    UINT8 = np.uint8

    @classmethod
    def from_rio(
        cls,
        dtype: str,
    ) -> DType:
        """Converts the rasterio data type to the data type.

        Parameters:
            dtype: rasterio data type

        Returns:
            data type
        """
        mapping = {
            rio.dtypes.bool_: DType.BOOL,
            rio.dtypes.float32: DType.FLOAT32,
            rio.dtypes.uint8: DType.UINT8,
        }
        return mapping[dtype]


class GeospatialFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    """
    Attributes:
        BILINEAR: bilinear mode
        NEAREST: nearest mode
    """
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'

    def to_rio(self) -> rio.enums.Resampling:
        """Converts the interpolation mode to the rasterio resampling mode.

        Returns:
            rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


@dataclass
class ProcessArea(Iterable[Coordinates]):
    """
    Attributes:
        coordinates: coordinates (x_min, y_min) of each tile
    """
    coordinates: CoordinatesSet

    def __init__(
        self,
        coordinates: CoordinatesSet = None,
    ) -> None:
        """
        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Raises:
            AviaryUserError: Invalid coordinates (`coordinates` is not an array of shape (n, 2) and data type int32)
        """
        self._coordinates = coordinates

        if self._coordinates is None:
            self._coordinates = np.empty(
                shape=(0, 2),
                dtype=np.int32,
            )

        conditions = [
            self._coordinates.ndim != 2,
            self._coordinates.shape[1] != 2,
            self._coordinates.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'coordinates must be an array of shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

    @property
    def coordinates(self) -> CoordinatesSet:
        """
        Returns:
            coordinates (x_min, y_min) of each tile
        """
        return self._coordinates

    @coordinates.setter
    def coordinates(
        self,
        value: CoordinatesSet,
    ) -> None:
        """
        Parameters:
            value: coordinates (x_min, y_min) of each tile

        Raises:
            AviaryUserError: Invalid coordinates (`coordinates` is not an array of shape (n, 2) and data type int32)
        """
        conditions = [
            value.ndim != 2,
            value.shape[1] != 2,
            value.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'coordinates must be an array of shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        self._coordinates = value

    @classmethod
    def from_bounding_box(
        cls,
        bounding_box: BoundingBox,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> ProcessArea:
        """Creates a process area from a bounding box.

        Parameters:
            bounding_box: bounding box
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            process area
        """
        coordinates = compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            quantize=quantize,
        )
        return cls(
            coordinates=coordinates,
        )

    @classmethod
    def from_gdf(
        cls,
        gdf: gpd.GeoDataFrame,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> ProcessArea:
        """Creates a process area from a geodataframe.

        Parameters:
            gdf: geodataframe
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            process area
        """
        bounding_box = BoundingBox.from_gdf(gdf)
        coordinates = compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            quantize=quantize,
        )
        coordinates = geospatial_filter(
            coordinates=coordinates,
            tile_size=tile_size,
            gdf=gdf,
            mode=GeospatialFilterMode.INTERSECTION,
        )
        return cls(
            coordinates=coordinates,
        )

    @classmethod
    def from_json(
        cls,
        json_string: str,
    ) -> ProcessArea:
        """Creates a process area from a JSON string.

        Parameters:
            json_string: JSON string

        Returns:
            process area
        """
        coordinates = json.loads(json_string)

        if coordinates:
            coordinates = np.array(coordinates, dtype=np.int32)
        else:
            coordinates = None

        return cls(
            coordinates=coordinates,
        )

    @classmethod
    def from_config(
        cls,
        config: ProcessAreaConfig,
    ) -> ProcessArea:
        """Creates a process area from the configuration.

        Parameters:
            config: configuration

        Returns:
            process area
        """
        if config.json_string is not None:
            process_area = cls.from_json(
                json_string=cast(str, config.json_string),
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

        if config.gdf is not None:
            process_area = cls.from_gdf(
                gdf=cast(gpd.GeoDataFrame, config.gdf),
                tile_size=config.tile_size,
                quantize=config.quantize,
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

        if config.bounding_box is not None:
            process_area = cls.from_bounding_box(
                bounding_box=cast(BoundingBox, config.bounding_box),
                tile_size=config.tile_size,
                quantize=config.quantize,
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            number of coordinates
        """
        return len(self._coordinates)

    def __getitem__(
        self,
        index: int,
    ) -> Coordinates:
        """Returns the coordinates given the index.

        Parameters:
            index: index of the coordinates

        Returns:
            coordinates
        """
        x_min, y_min = self._coordinates[index]
        return x_min, y_min

    def __iter__(self) -> Iterator[Coordinates]:
        """Iterates over the coordinates.

        Yields:
            coordinates
        """
        for x_min, y_min in self._coordinates:
            yield x_min, y_min

    def __add__(
        self,
        other: ProcessArea,
    ) -> ProcessArea:
        """Adds the coordinates.

        Notes:
            - This method is equivalent to applying the set filter with the `UNION` set filter mode
              to the coordinates

        Parameters:
            other: other process area

        Returns:
            union of the process areas
        """
        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.UNION,
        )
        return ProcessArea(
            coordinates=coordinates,
        )

    def __sub__(
        self,
        other: ProcessArea,
    ) -> ProcessArea:
        """Subtracts the coordinates.

        Notes:
            - This method is equivalent to applying the set filter with the `DIFFERENCE` set filter mode
              to the coordinates

        Parameters:
            other: other process area

        Returns:
            difference of the process areas
        """
        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.DIFFERENCE,
        )
        return ProcessArea(
            coordinates=coordinates,
        )

    def append(
        self,
        other: Coordinates,
        inplace: bool = False,
    ) -> ProcessArea:
        """Appends the coordinates.

        Parameters:
            other: other coordinates
            inplace: if True, the coordinates are appended inplace

        Returns:
            process area
        """
        other = np.array([other], dtype=np.int32)
        coordinates = np.concatenate([self._coordinates, other], axis=0)
        coordinates = duplicates_filter(coordinates)

        if inplace:
            self.coordinates = coordinates
            return self
        else:
            return ProcessArea(
                coordinates=coordinates,
            )

    def chunk(
        self,
        num_chunks: int,
    ) -> list[ProcessArea]:
        """Chunks the coordinates.

        Parameters:
            num_chunks: number of chunks

        Returns:
            list of process areas
        """
        return [
            ProcessArea(
                coordinates=coordinates,
            )
            for coordinates
            in np.array_split(self._coordinates, indices_or_sections=num_chunks)
        ]

    def filter(
        self,
        coordinates_filter: CoordinatesFilter,
        inplace: bool = False,
    ) -> ProcessArea:
        """Filters the coordinates.

        Parameters:
            coordinates_filter: coordinates filter
            inplace: if True, the coordinates are filtered inplace

        Returns:
            filtered process area
        """
        coordinates = coordinates_filter(self._coordinates)

        if inplace:
            self.coordinates = coordinates
            return self
        else:
            return ProcessArea(
                coordinates=coordinates,
            )

    def to_gdf(
        self,
        epsg_code: EPSGCode,
        tile_size: TileSize,
    ) -> gpd.GeoDataFrame:
        """Converts the coordinates to a geodataframe.

        Parameters:
            epsg_code: EPSG code
            tile_size: tile size in meters

        Returns:
            geodataframe

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` <= 0)
        """
        if tile_size <= 0:
            message = (
                'Invalid tile size! '
                'tile_size must be positive.'
            )
            raise AviaryUserError(message)

        geometry = [
            box(x_min, y_min, x_min + tile_size, y_min + tile_size)
            for x_min, y_min in self._coordinates
        ]
        return gpd.GeoDataFrame(
            geometry=geometry,
            crs=f'EPSG:{epsg_code}',
        )

    def to_json(self) -> str:
        """Converts the coordinates to a JSON string.

        Returns:
            JSON string
        """
        return str(self._coordinates.tolist())


class ProcessAreaConfig(pydantic.BaseModel):
    """Configuration for the `from_config` classmethod of `ProcessArea`

    The configuration must have one of the following field sets:
        - `json_string`
        - `gdf` and `tile_size`
        - `bounding_box` and `tile_size`

    Attributes:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
        gdf: path to the geodataframe
        json_string: path to the JSON file
        processed_coordinates_json_string: path to the JSON file containing the coordinates of the processed tiles
        tile_size: tile size in meters
        quantize: if True, the bounding box is quantized to `tile_size`
    """
    bounding_box: list[Coordinate] | None = None
    gdf: Path | None = None
    json_string: Path | None = None
    processed_coordinates_json_string: Path | None = None
    tile_size: TileSize | None = None
    quantize: bool = True

    # noinspection PyNestedDecorators
    @pydantic.field_validator('bounding_box')
    @classmethod
    def parse_bounding_box(
        cls,
        bounding_box: list[Coordinate],
    ) -> BoundingBox:
        """Parses the bounding box."""
        if len(bounding_box) != 4:
            message = (
                'Invalid bounding box! '
                'bounding_box must be a list of length 4.'
            )
            raise ValueError(message)

        return BoundingBox(
            x_min=bounding_box[0],
            y_min=bounding_box[1],
            x_max=bounding_box[2],
            y_max=bounding_box[3],
        )

    # noinspection PyNestedDecorators
    @pydantic.field_validator('gdf')
    @classmethod
    def parse_gdf(
        cls,
        gdf: Path,
    ) -> gpd.GeoDataFrame:
        """Parses the geodataframe."""
        return gpd.read_file(gdf)

    # noinspection PyNestedDecorators
    @pydantic.field_validator('json_string')
    @classmethod
    def parse_json_string(
        cls,
        json_string: Path,
    ) -> str:
        """Parses the JSON string."""
        with open(json_string, 'r') as file:
            return file.read()

    # noinspection PyNestedDecorators
    @pydantic.field_validator('processed_coordinates_json_string')
    @classmethod
    def parse_processed_coordinates_json_string(
        cls,
        processed_coordinates_json_string: Path,
    ) -> str:
        """Parses the JSON string containing the coordinates of the processed tiles."""
        with open(processed_coordinates_json_string, 'r') as file:
            return file.read()

    @pydantic.model_validator(mode='after')
    def validate(self) -> ProcessAreaConfig:
        """Validates the configuration."""
        conditions = [
            self.json_string is not None,
            self.gdf is not None and self.tile_size is not None,
            self.bounding_box is not None and self.tile_size is not None,
        ]

        if any(conditions) is False:
            message = (
                'Invalid configuration! '
                'config must have one of the following field sets: '
                'json_string | gdf, tile_size | bounding_box, tile_size'
            )
            raise ValueError(message)

        return self


class SegmentationExporterMode(Enum):
    """
    Attributes:
        FEATHER: feather mode
        GPKG: geopackage mode
    """
    FEATHER = 'feather'
    GPKG = 'gpkg'


class SetFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
        UNION: union mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
